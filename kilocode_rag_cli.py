#!/usr/bin/env python3
"""
KiloCodeRAG MCP CLI接口
提供命令行界面來使用KiloCodeRAG的所有功能
"""

import os
import sys
import json
import asyncio
import argparse
import logging
from typing import Dict, List, Any, Optional
from pathlib import Path
from datetime import datetime

# 添加項目路徑
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# 設置日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class KiloCodeRAGCLI:
    """KiloCodeRAG MCP CLI接口"""
    
    def __init__(self):
        """初始化CLI"""
        self.capability_manager = None
        self.rag_system = None
        self.kilocode_adapter = None
        
        # 初始化組件
        self._init_components()
    
    def _init_components(self):
        """初始化組件"""
        try:
            # 導入功能管理器
            from kilocode_rag_capability_manager import KiloCodeRAGCapabilityManager
            self.capability_manager = KiloCodeRAGCapabilityManager()
            
            # 導入RAG系統
            from fixed_kilorag_integration_system import FixedKiloRAGIntegrationSystem
            self.rag_system = FixedKiloRAGIntegrationSystem()
            
            # 導入KiloCode適配器
            from mcptool.adapters.simple_kilocode_adapter import SimpleKiloCodeAdapter
            self.kilocode_adapter = SimpleKiloCodeAdapter()
            
            logger.info("KiloCodeRAG CLI組件初始化完成")
            
        except Exception as e:
            logger.error(f"組件初始化失敗: {e}")
            print(f"❌ 初始化失敗: {e}")
            sys.exit(1)
    
    def list_capabilities(self, category: Optional[str] = None, format: str = "simple"):
        """列出功能列表"""
        print("\\n🔧 KiloCodeRAG MCP 功能列表")
        print("=" * 50)
        
        try:
            result = self.capability_manager.get_capability_list(category, format)
            
            if result["status"] != "success":
                print(f"❌ 獲取功能列表失敗: {result.get('message', 'Unknown error')}")
                return
            
            capabilities = result["capabilities"]
            
            if format == "simple":
                for cat_name, cat_info in capabilities.items():
                    print(f"\\n🔹 {cat_info['name']}")
                    print(f"   描述: {cat_info['description']}")
                    print(f"   功能數量: {cat_info['function_count']}")
                    
                    # 顯示功能列表
                    functions = cat_info['functions']
                    if len(functions) <= 3:
                        print(f"   功能: {', '.join(functions)}")
                    else:
                        print(f"   功能: {', '.join(functions[:3])}... (共{len(functions)}個)")
            else:
                # 詳細格式
                for cat_name, cat_info in capabilities.items():
                    print(f"\\n🔹 {cat_info['name']}")
                    print(f"   描述: {cat_info['description']}")
                    
                    for func in cat_info['functions']:
                        print(f"\\n   • {func['name']} ({func['id']})")
                        print(f"     描述: {func['description']}")
                        print(f"     用途: {func['usage']}")
                        print(f"     示例: {func['example']}")
            
            print(f"\\n📊 總計: {result['total_categories']} 個分類, {result['total_functions']} 個功能")
            
        except Exception as e:
            print(f"❌ 列出功能失敗: {e}")
    
    def search_functions(self, query: str):
        """搜索功能"""
        print(f"\\n🔍 搜索功能: '{query}'")
        print("=" * 50)
        
        try:
            result = self.capability_manager.search_functions(query)
            
            if result["status"] != "success":
                print(f"❌ 搜索失敗: {result.get('message', 'Unknown error')}")
                return
            
            results = result["results"]
            
            if not results:
                print("❌ 沒有找到相關功能")
                return
            
            print(f"✅ 找到 {len(results)} 個相關功能:")
            
            for i, func in enumerate(results, 1):
                print(f"\\n{i}. {func['name']} ({func['function_id']})")
                print(f"   分類: {func['category_name']}")
                print(f"   描述: {func['description']}")
                print(f"   相關性: {func['relevance_score']}")
            
        except Exception as e:
            print(f"❌ 搜索功能失敗: {e}")
    
    def get_function_info(self, function_id: str):
        """獲取功能詳情"""
        print(f"\\n📋 功能詳情: {function_id}")
        print("=" * 50)
        
        try:
            result = self.capability_manager.get_function_details(function_id)
            
            if result["status"] != "success":
                print(f"❌ 獲取功能詳情失敗: {result.get('message', 'Unknown error')}")
                return
            
            func = result["function"]
            
            print(f"名稱: {func['name']}")
            print(f"ID: {func['id']}")
            print(f"分類: {result['category_name']} ({result['category']})")
            print(f"描述: {func['description']}")
            print(f"用途: {func['usage']}")
            print(f"示例: {func['example']}")
            print(f"參數: {', '.join(func['parameters'])}")
            print(f"輸出: {func['output']}")
            print(f"使用次數: {result['usage_count']}")
            
        except Exception as e:
            print(f"❌ 獲取功能詳情失敗: {e}")
    
    async def search_knowledge(self, query: str, limit: int = 5):
        """搜索知識庫"""
        print(f"\\n🔍 知識庫搜索: '{query}'")
        print("=" * 50)
        
        try:
            result = await self.rag_system.search_knowledge(query, limit)
            
            if result["status"] != "success":
                print(f"❌ 知識搜索失敗: {result.get('error', 'Unknown error')}")
                return
            
            results = result["results"]
            
            if not results:
                print("❌ 沒有找到相關知識")
                return
            
            print(f"✅ 找到 {result['total_results']} 個相關結果 (查詢時間: {result['query_time']:.3f}s):")
            
            for i, item in enumerate(results, 1):
                print(f"\\n{i}. 記憶ID: {item['memory_id']}")
                print(f"   內容: {item['content']}")
                print(f"   相關性: {item['score']:.3f}")
                
                if 'metadata' in item and item['metadata']:
                    metadata = item['metadata']
                    if 'content_type' in metadata:
                        print(f"   類型: {metadata['content_type']}")
                    if 'file_path' in metadata:
                        print(f"   文件: {metadata['file_path']}")
            
        except Exception as e:
            print(f"❌ 知識搜索失敗: {e}")
    
    def execute_kilocode(self, question: str):
        """執行KiloCode動態工具創建"""
        print(f"\\n⚡ KiloCode執行: '{question}'")
        print("=" * 50)
        
        try:
            result = self.kilocode_adapter.process(question)
            
            print("✅ KiloCode執行結果:")
            print(result)
            
            # 記錄使用統計
            self.capability_manager.record_usage("kilocode_execution")
            
        except Exception as e:
            print(f"❌ KiloCode執行失敗: {e}")
    
    async def get_system_status(self):
        """獲取系統狀態"""
        print("\\n📊 KiloCodeRAG系統狀態")
        print("=" * 50)
        
        try:
            # RAG系統狀態
            rag_status = await self.rag_system.get_system_status()
            
            print("🗄️ RAG系統:")
            if rag_status["status"] == "active":
                print(f"   已索引文件: {rag_status['indexed_files']}")
                print(f"   已索引交互: {rag_status['indexed_interactions']}")
                print(f"   總查詢次數: {rag_status['total_queries']}")
                print(f"   RAG記憶數量: {rag_status['rag_memories_count']}")
            else:
                print(f"   狀態: 錯誤 - {rag_status.get('error', 'Unknown error')}")
            
            # 功能使用統計
            usage_stats = self.capability_manager.get_usage_statistics()
            
            print("\\n📈 功能使用統計:")
            if usage_stats["status"] == "success":
                print(f"   總使用次數: {usage_stats['total_usage']}")
                print(f"   使用過的功能: {usage_stats['unique_functions_used']}")
                
                if usage_stats['most_used_functions']:
                    print("   最常用功能:")
                    for func in usage_stats['most_used_functions'][:3]:
                        print(f"     • {func['name']}: {func['usage_count']} 次")
            else:
                print(f"   狀態: 錯誤 - {usage_stats.get('message', 'Unknown error')}")
            
            print(f"\\n🕒 最後更新: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            
        except Exception as e:
            print(f"❌ 獲取系統狀態失敗: {e}")
    
    async def index_files(self):
        """索引項目文件"""
        print("\\n📁 開始索引項目文件...")
        print("=" * 50)
        
        try:
            result = await self.rag_system.scan_and_index_all_files()
            
            print(f"✅ 文件索引完成:")
            print(f"   總文件數: {result['total_files']}")
            print(f"   成功索引: {result['indexed_files']}")
            print(f"   跳過文件: {result['skipped_files']}")
            print(f"   失敗文件: {result['failed_files']}")
            
            if result['file_types']:
                print("\\n   文件類型分佈:")
                for ext, count in sorted(result['file_types'].items()):
                    print(f"     {ext}: {count}")
            
            if result['errors']:
                print(f"\\n   錯誤信息 (前5個):")
                for error in result['errors'][:5]:
                    print(f"     • {error}")
            
        except Exception as e:
            print(f"❌ 文件索引失敗: {e}")


def create_parser():
    """創建命令行解析器"""
    parser = argparse.ArgumentParser(
        description="KiloCodeRAG MCP CLI - 智能工具和知識檢索命令行界面",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法:
  %(prog)s list                          # 列出所有功能
  %(prog)s list --category kilocode_functions --format detailed  # 詳細列出KiloCode功能
  %(prog)s search "計算"                  # 搜索計算相關功能
  %(prog)s info create_calculator        # 獲取計算器功能詳情
  %(prog)s knowledge "GAIA測試"          # 搜索知識庫
  %(prog)s execute "計算2+2*3"           # 執行KiloCode
  %(prog)s status                        # 查看系統狀態
  %(prog)s index                         # 索引項目文件
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    
    # list命令
    list_parser = subparsers.add_parser('list', help='列出功能列表')
    list_parser.add_argument('--category', help='功能分類過濾')
    list_parser.add_argument('--format', choices=['simple', 'detailed'], default='simple', help='顯示格式')
    
    # search命令
    search_parser = subparsers.add_parser('search', help='搜索功能')
    search_parser.add_argument('query', help='搜索關鍵詞')
    
    # info命令
    info_parser = subparsers.add_parser('info', help='獲取功能詳情')
    info_parser.add_argument('function_id', help='功能ID')
    
    # knowledge命令
    knowledge_parser = subparsers.add_parser('knowledge', help='搜索知識庫')
    knowledge_parser.add_argument('query', help='搜索關鍵詞')
    knowledge_parser.add_argument('--limit', type=int, default=5, help='結果數量限制')
    
    # execute命令
    execute_parser = subparsers.add_parser('execute', help='執行KiloCode')
    execute_parser.add_argument('question', help='要處理的問題')
    
    # status命令
    subparsers.add_parser('status', help='查看系統狀態')
    
    # index命令
    subparsers.add_parser('index', help='索引項目文件')
    
    return parser


async def main():
    """主函數"""
    parser = create_parser()
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # 初始化CLI
    cli = KiloCodeRAGCLI()
    
    try:
        if args.command == 'list':
            cli.list_capabilities(args.category, args.format)
        
        elif args.command == 'search':
            cli.search_functions(args.query)
        
        elif args.command == 'info':
            cli.get_function_info(args.function_id)
        
        elif args.command == 'knowledge':
            await cli.search_knowledge(args.query, args.limit)
        
        elif args.command == 'execute':
            cli.execute_kilocode(args.question)
        
        elif args.command == 'status':
            await cli.get_system_status()
        
        elif args.command == 'index':
            await cli.index_files()
        
        else:
            print(f"❌ 未知命令: {args.command}")
            parser.print_help()
    
    except KeyboardInterrupt:
        print("\\n\\n⚠️ 用戶中斷操作")
    except Exception as e:
        print(f"\\n❌ 執行失敗: {e}")
        logger.error(f"CLI執行失敗: {e}", exc_info=True)


if __name__ == "__main__":
    asyncio.run(main())

