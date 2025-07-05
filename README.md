# ArcticCloud VPS 自动续期脚本

使用 GitHub Actions 每 3 天自动运行，支持 Telegram 推送，支持 SOCKS5 全局代理访问。

## 📦 环境变量配置（GitHub Secret）

- `ArcticCloud_CONFIG`：格式如下
```json
{
  "username": "your_username",
  "password": "your_password",
  "VPS": {
    "DE-Frankfurt": 122,
    "UK-Portsmouth": 123
  }
}