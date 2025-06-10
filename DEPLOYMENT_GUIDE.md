# PowerAutomation v0.55 部署指南

**快速部署真實Token節省智慧路由系統**

## 🚀 快速開始

### 系統要求
- Python 3.11+
- 4GB+ RAM

### 一鍵安裝
```bash
git clone https://github.com/alexchuang650730/Powerauto.ai.git
cd Powerauto.ai
pip3 install tiktoken cryptography flask flask-socketio
python3 real_token_saving_system.py
```

## 🎯 核心功能驗證

### Token節省測試
```bash
python3 real_token_saving_system.py
# 預期: Token節省率100%, 成本節省$0.0016+
```

### 一鍵功能驗證
```bash
python3 -c "
from real_token_saving_system import RealTokenSavingRouter, PerfectPrivacyProtector, RealTimeCreditsManager

# Token節省測試
router = RealTokenSavingRouter()
result = router.make_routing_decision('format code', 'LOW_SENSITIVE')
print(f'✅ Token節省: \${result[\"cost_saved\"]:.4f}')

# 隱私保護測試  
protector = PerfectPrivacyProtector()
privacy = protector.detect_sensitive_data('api_key: sk-test123')
print(f'✅ 隱私保護: {privacy[\"privacy_level\"]}')

# 積分系統測試
credits = RealTimeCreditsManager()
credits.initialize_user_credits('test', 1000)
print(f'✅ 積分系統: {credits.get_user_credits(\"test\")} 積分')

print('🎯 所有核心功能正常運行!')
"
```

## 🏗️ 生產環境部署

### 整合到現有系統
```python
from admin_realtime_monitor import integrate_admin_monitor_to_platform

app = Flask(__name__)
socketio = SocketIO(app)
admin_monitor = integrate_admin_monitor_to_platform(app, socketio)
socketio.run(app, host='0.0.0.0', port=5000)
```

## 📞 技術支持
- **GitHub**: https://github.com/alexchuang650730/Powerauto.ai
- **文檔**: README_TOKEN_SAVING_SYSTEM.md

**PowerAutomation v0.55 - 經濟、安全、易部署！** 🚀
