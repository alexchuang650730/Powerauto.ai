#!/usr/bin/env python3
"""
動態網絡配置管理器 - PowerAutomation v0.5.2
支持動態端口發現和靈活IPv6配置
"""

import socket
import subprocess
import json
import time
import logging
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path
import threading
import asyncio


@dataclass
class NetworkConfig:
    """網絡配置數據類"""
    ipv6_address: str
    port: int
    interface: str
    scope: str
    is_available: bool = False
    last_check: float = 0.0


class DynamicNetworkManager:
    """動態網絡配置管理器"""
    
    def __init__(self, config_file: str = "network_config.json"):
        self.config_file = Path(config_file)
        self.logger = self._setup_logger()
        self.preferred_ports = [5001, 5002, 5003, 8080, 8081, 8082, 9000, 9001]
        self.port_range = (5000, 9999)
        self.current_config: Optional[NetworkConfig] = None
        self.config_lock = threading.Lock()
        
    def _setup_logger(self) -> logging.Logger:
        """設置日誌記錄器"""
        logger = logging.getLogger("DynamicNetworkManager")
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    def discover_ipv6_addresses(self) -> List[NetworkConfig]:
        """發現系統可用的IPv6地址"""
        ipv6_configs = []
        
        try:
            # 使用ip命令獲取IPv6地址
            result = subprocess.run(
                ['ip', '-6', 'addr', 'show'], 
                capture_output=True, 
                text=True, 
                timeout=10
            )
            
            if result.returncode != 0:
                self.logger.warning("無法執行ip命令獲取IPv6地址")
                return self._get_fallback_ipv6_configs()
            
            # 解析ip命令輸出
            current_interface = None
            for line in result.stdout.split('\n'):
                line = line.strip()
                
                # 解析接口名稱
                if ':' in line and '<' in line:
                    parts = line.split(':')
                    if len(parts) >= 2:
                        current_interface = parts[1].split()[0]
                
                # 解析IPv6地址
                if line.startswith('inet6') and current_interface:
                    parts = line.split()
                    if len(parts) >= 4:
                        ipv6_addr = parts[1].split('/')[0]
                        scope = parts[-1] if parts[-1] in ['host', 'link', 'global'] else 'unknown'
                        
                        config = NetworkConfig(
                            ipv6_address=ipv6_addr,
                            port=0,  # 稍後分配
                            interface=current_interface,
                            scope=scope
                        )
                        ipv6_configs.append(config)
            
            self.logger.info(f"發現 {len(ipv6_configs)} 個IPv6地址")
            return ipv6_configs
            
        except Exception as e:
            self.logger.error(f"發現IPv6地址時出錯: {e}")
            return self._get_fallback_ipv6_configs()
    
    def _get_fallback_ipv6_configs(self) -> List[NetworkConfig]:
        """獲取備用IPv6配置"""
        fallback_configs = [
            NetworkConfig("::1", 0, "lo", "host"),  # 本地回環
            NetworkConfig("::", 0, "all", "global"),  # 所有地址
        ]
        
        # 嘗試獲取鏈路本地地址
        try:
            sock = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)
            sock.connect(("2001:db8::1", 80))  # 測試地址
            local_addr = sock.getsockname()[0]
            if local_addr and local_addr not in ["::1", "::"]:
                fallback_configs.append(
                    NetworkConfig(local_addr, 0, "auto", "link")
                )
            sock.close()
        except:
            pass
        
        return fallback_configs
    
    def find_available_port(self, ipv6_address: str, preferred_ports: List[int] = None) -> Optional[int]:
        """為指定IPv6地址找到可用端口"""
        if preferred_ports is None:
            preferred_ports = self.preferred_ports
        
        # 首先嘗試首選端口
        for port in preferred_ports:
            if self._test_port_availability(ipv6_address, port):
                return port
        
        # 如果首選端口都不可用，動態搜索
        return self._dynamic_port_search(ipv6_address)
    
    def _test_port_availability(self, ipv6_address: str, port: int) -> bool:
        """測試端口是否可用"""
        try:
            sock = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.settimeout(2.0)
            
            # 嘗試綁定
            sock.bind((ipv6_address, port))
            sock.listen(1)
            sock.close()
            
            self.logger.debug(f"端口 {port} 在 [{ipv6_address}] 上可用")
            return True
            
        except Exception as e:
            self.logger.debug(f"端口 {port} 在 [{ipv6_address}] 上不可用: {e}")
            return False
    
    def _dynamic_port_search(self, ipv6_address: str) -> Optional[int]:
        """動態搜索可用端口"""
        start_port, end_port = self.port_range
        
        # 隨機起始點，避免總是從同一個端口開始
        import random
        start_search = random.randint(start_port, end_port - 1000)
        
        # 向上搜索
        for port in range(start_search, end_port):
            if self._test_port_availability(ipv6_address, port):
                self.logger.info(f"動態發現可用端口: {port}")
                return port
        
        # 向下搜索
        for port in range(start_search - 1, start_port - 1, -1):
            if self._test_port_availability(ipv6_address, port):
                self.logger.info(f"動態發現可用端口: {port}")
                return port
        
        return None
    
    def get_optimal_config(self) -> Optional[NetworkConfig]:
        """獲取最優網絡配置"""
        ipv6_configs = self.discover_ipv6_addresses()
        
        # 按優先級排序IPv6地址
        priority_order = {
            'global': 1,  # 全局地址優先
            'link': 2,    # 鏈路本地地址次之
            'host': 3     # 本地回環最後
        }
        
        ipv6_configs.sort(key=lambda x: (
            priority_order.get(x.scope, 99),
            x.ipv6_address == "::",  # :: 地址排在後面
            x.ipv6_address
        ))
        
        # 為每個IPv6地址尋找可用端口
        for config in ipv6_configs:
            available_port = self.find_available_port(config.ipv6_address)
            if available_port:
                config.port = available_port
                config.is_available = True
                config.last_check = time.time()
                
                self.logger.info(
                    f"找到最優配置: [{config.ipv6_address}]:{config.port} "
                    f"(接口: {config.interface}, 範圍: {config.scope})"
                )
                return config
        
        self.logger.error("無法找到可用的網絡配置")
        return None
    
    def save_config(self, config: NetworkConfig) -> bool:
        """保存網絡配置到文件"""
        try:
            config_data = {
                "ipv6_address": config.ipv6_address,
                "port": config.port,
                "interface": config.interface,
                "scope": config.scope,
                "is_available": config.is_available,
                "last_check": config.last_check,
                "timestamp": time.time()
            }
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"網絡配置已保存到 {self.config_file}")
            return True
            
        except Exception as e:
            self.logger.error(f"保存配置失敗: {e}")
            return False
    
    def load_config(self) -> Optional[NetworkConfig]:
        """從文件加載網絡配置"""
        try:
            if not self.config_file.exists():
                return None
            
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
            
            config = NetworkConfig(
                ipv6_address=config_data["ipv6_address"],
                port=config_data["port"],
                interface=config_data["interface"],
                scope=config_data["scope"],
                is_available=config_data.get("is_available", False),
                last_check=config_data.get("last_check", 0.0)
            )
            
            # 驗證配置是否仍然有效
            if self._validate_config(config):
                self.logger.info(f"加載有效配置: [{config.ipv6_address}]:{config.port}")
                return config
            else:
                self.logger.warning("已保存的配置不再有效，需要重新配置")
                return None
                
        except Exception as e:
            self.logger.error(f"加載配置失敗: {e}")
            return None
    
    def _validate_config(self, config: NetworkConfig) -> bool:
        """驗證配置是否仍然有效"""
        # 檢查配置是否過期（超過1小時）
        if time.time() - config.last_check > 3600:
            return False
        
        # 測試端口是否仍然可用
        return self._test_port_availability(config.ipv6_address, config.port)
    
    def get_or_create_config(self) -> Optional[NetworkConfig]:
        """獲取或創建網絡配置"""
        with self.config_lock:
            # 嘗試加載現有配置
            config = self.load_config()
            if config:
                self.current_config = config
                return config
            
            # 創建新配置
            config = self.get_optimal_config()
            if config:
                self.save_config(config)
                self.current_config = config
                return config
            
            return None
    
    def refresh_config(self) -> Optional[NetworkConfig]:
        """刷新網絡配置"""
        with self.config_lock:
            self.logger.info("刷新網絡配置...")
            config = self.get_optimal_config()
            if config:
                self.save_config(config)
                self.current_config = config
                return config
            return None
    
    def get_config_info(self) -> Dict:
        """獲取配置信息"""
        if not self.current_config:
            return {"status": "no_config", "message": "沒有可用的網絡配置"}
        
        return {
            "status": "active",
            "ipv6_address": self.current_config.ipv6_address,
            "port": self.current_config.port,
            "interface": self.current_config.interface,
            "scope": self.current_config.scope,
            "endpoint": f"http://[{self.current_config.ipv6_address}]:{self.current_config.port}",
            "last_check": self.current_config.last_check,
            "is_available": self.current_config.is_available
        }


class EdgeAdminServer:
    """端側Admin服務器 - 支持動態網絡配置"""
    
    def __init__(self):
        self.network_manager = DynamicNetworkManager()
        self.server_socket = None
        self.is_running = False
        self.logger = logging.getLogger("EdgeAdminServer")
        
    async def start_server(self) -> bool:
        """啟動服務器"""
        try:
            # 獲取網絡配置
            config = self.network_manager.get_or_create_config()
            if not config:
                self.logger.error("無法獲取有效的網絡配置")
                return False
            
            # 創建服務器socket
            self.server_socket = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            
            # 綁定地址和端口
            self.server_socket.bind((config.ipv6_address, config.port))
            self.server_socket.listen(10)
            
            self.is_running = True
            
            self.logger.info(
                f"🚀 端側Admin服務器已啟動: "
                f"http://[{config.ipv6_address}]:{config.port}"
            )
            
            # 啟動服務循環
            await self._server_loop()
            
            return True
            
        except Exception as e:
            self.logger.error(f"啟動服務器失敗: {e}")
            return False
    
    async def _server_loop(self):
        """服務器主循環"""
        while self.is_running:
            try:
                # 這裡可以添加實際的服務邏輯
                await asyncio.sleep(1)
                
            except Exception as e:
                self.logger.error(f"服務器循環錯誤: {e}")
                break
    
    def stop_server(self):
        """停止服務器"""
        self.is_running = False
        if self.server_socket:
            self.server_socket.close()
        self.logger.info("端側Admin服務器已停止")
    
    def get_server_info(self) -> Dict:
        """獲取服務器信息"""
        config_info = self.network_manager.get_config_info()
        config_info.update({
            "server_status": "running" if self.is_running else "stopped",
            "server_type": "EdgeAdminServer",
            "version": "v0.5.2"
        })
        return config_info


def main():
    """主函數 - 演示動態網絡配置"""
    print("🌐 PowerAutomation v0.5.2 動態網絡配置管理器")
    print("=" * 60)
    
    # 創建網絡管理器
    network_manager = DynamicNetworkManager()
    
    # 發現IPv6地址
    print("\n🔍 發現系統IPv6地址:")
    ipv6_configs = network_manager.discover_ipv6_addresses()
    for i, config in enumerate(ipv6_configs, 1):
        print(f"  {i}. [{config.ipv6_address}] (接口: {config.interface}, 範圍: {config.scope})")
    
    # 獲取最優配置
    print("\n⚡ 獲取最優網絡配置:")
    optimal_config = network_manager.get_optimal_config()
    if optimal_config:
        print(f"  ✅ 最優配置: [{optimal_config.ipv6_address}]:{optimal_config.port}")
        print(f"     接口: {optimal_config.interface}")
        print(f"     範圍: {optimal_config.scope}")
        print(f"     端點: http://[{optimal_config.ipv6_address}]:{optimal_config.port}")
        
        # 保存配置
        network_manager.save_config(optimal_config)
        print(f"  💾 配置已保存到: {network_manager.config_file}")
        
    else:
        print("  ❌ 無法找到可用的網絡配置")
    
    # 測試服務器啟動
    print("\n🚀 測試端側Admin服務器:")
    server = EdgeAdminServer()
    
    async def test_server():
        success = await server.start_server()
        if success:
            print("  ✅ 服務器啟動成功")
            
            # 顯示服務器信息
            info = server.get_server_info()
            print(f"  📊 服務器信息:")
            for key, value in info.items():
                print(f"     {key}: {value}")
            
            # 運行5秒後停止
            await asyncio.sleep(5)
            server.stop_server()
            print("  🛑 服務器已停止")
        else:
            print("  ❌ 服務器啟動失敗")
    
    # 運行測試
    asyncio.run(test_server())
    
    print("\n✨ 動態網絡配置測試完成!")


if __name__ == "__main__":
    main()

