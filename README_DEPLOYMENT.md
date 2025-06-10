# PowerAutomation v0.5.2 本地部署指南

## 🚀 快速開始

### 1. 環境要求
- **Python**: 3.8+ 版本
- **操作系統**: Windows 10+, macOS 12+, Ubuntu 20.04+
- **網絡**: 支持IPv6（本地環境自動配置）

### 2. 文件清單
```
PowerAutomation v0.5.2/
├── dynamic_network_manager.py    # 動態網絡配置管理器
├── edge_cloud_simulator.py       # 端雲模擬環境
├── deploy.py                     # 一鍵部署腳本
├── README_DEPLOYMENT.md          # 本文檔
└── network_config.json           # 自動生成的網絡配置
```

### 3. 一鍵啟動
```bash
# 方法1: 使用部署腳本
python3 deploy.py

# 方法2: 直接啟動
python3 edge_cloud_simulator.py
```

## 📊 服務架構

### 端側Admin服務
- **功能**: MCP適配器管理、本地數據處理
- **端口**: 動態分配（通常5001-5003）
- **Web界面**: http://[::1]:端口

### 雲側Admin服務  
- **功能**: 配置管理、監控告警、數據同步
- **端口**: 動態分配（通常6001-6003）
- **Web界面**: http://[::1]:端口

## 🔧 配置說明

### 動態端口配置
系統會自動：
1. 掃描可用IPv6地址
2. 測試端口可用性
3. 選擇最優配置
4. 保存到 `network_config.json`

### 首選端口列表
- 端側Admin: 5001, 5002, 5003
- 雲側Admin: 6001, 6002, 6003
- 備用範圍: 5000-9999

## 🌐 API端點

### 端側Admin API
```
GET  /                    # Web界面
GET  /health             # 健康檢查
GET  /api/discovery      # 服務發現
GET  /api/adapters       # 適配器列表
POST /api/mcp/call       # MCP調用
POST /api/sync/trigger   # 觸發同步
```

### 雲側Admin API
```
GET  /                    # Web界面
GET  /health             # 健康檢查
GET  /api/config         # 配置管理
GET  /api/monitor        # 監控數據
POST /api/sync/receive   # 接收同步
POST /api/config/update  # 更新配置
```

## 🧪 測試驗證

### 1. 健康檢查
```bash
# 端側Admin
curl http://[::1]:5002/health

# 雲側Admin  
curl http://[::1]:6001/health
```

### 2. MCP調用測試
```bash
curl -X POST http://[::1]:5002/api/mcp/call \
  -H "Content-Type: application/json" \
  -d '{
    "adapter": "simple_gemini",
    "method": "generate_text", 
    "params": {"prompt": "Hello World"}
  }'
```

### 3. 同步測試
```bash
curl -X POST http://[::1]:5002/api/sync/trigger
```

## 🔍 故障排除

### 常見問題

**Q: 端口被占用怎麼辦？**
A: 系統會自動尋找可用端口，無需手動處理

**Q: IPv6不支持怎麼辦？**
A: 系統會自動回退到本地IPv6 (::1)

**Q: 服務啟動失敗？**
A: 檢查Python版本和文件完整性

### 日誌查看
服務運行時會在控制台輸出詳細日誌：
- INFO: 正常操作信息
- WARNING: 警告信息
- ERROR: 錯誤信息

## 📱 Web界面功能

### 端側Admin界面
- 服務狀態監控
- 適配器管理
- MCP調用歷史
- 雲側連接狀態

### 雲側Admin界面
- 全局配置管理
- 端側設備列表
- 同步操作監控
- 性能指標展示

## 🚀 生產部署準備

### 雲服務器部署
當本地測試通過後，可以將雲側Admin部署到雲服務器：

1. **租用雲服務器**（支持IPv6）
2. **配置域名和SSL證書**
3. **修改端側Admin配置**指向雲服務器
4. **設置防火牆和安全組**
5. **配置監控和日誌**

### 配置修改
```python
# 修改 edge_cloud_simulator.py 中的雲側端點
CLOUD_ADMIN_ENDPOINT = "https://your-cloud-server.com:6001"
```

## 📞 技術支持

- **GitHub Issues**: 報告問題和建議
- **文檔Wiki**: 詳細技術文檔
- **社區討論**: 技術交流和分享

---

**PowerAutomation v0.5.2 - 讓AI自動化觸手可及**

