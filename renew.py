# -- coding: utf-8 --
import os
import json
from curl_cffi import requests

# =========================
# SOCKS5 代理
# =========================
socks5_proxy = os.environ.get("SOCKS5_PROXY", "")
proxies = {
    "http": socks5_proxy,
    "https": socks5_proxy
} if socks5_proxy else {}

# =========================
# 读取 ArcticCloud_CONFIG
# =========================
config = os.environ.get(
    "ArcticCloud_CONFIG",
    '{"username": "", "password": "", "VPS": {}}'
)

try:
    config = json.loads(config)
except json.JSONDecodeError as e:
    raise ValueError(f"解析 ArcticCloud_CONFIG 失败: {e}")

username = config.get("username", "")
password = config.get("password", "")

if not username or not password:
    print("❌ 账号或密码为空，退出脚本")
    exit(1)

# =========================
# 基础配置
# =========================
BASE_URL = "https://vps.polarbear.nyc.mn"
login_url = f"{BASE_URL}/index/login/?referer=%2Fcontrol%2Findex%2F"

telegram_bot_token = os.environ.get("TELEGRAM_BOT_TOKEN", "")
chat_id = os.environ.get("CHAT_ID", "")
thread_id = os.environ.get("THREAD_ID", "")
telegram_api_url = os.environ.get(
    "TELEGRAM_API_URL",
    "https://api.telegram.org"
)

# =========================
# Telegram 推送
# =========================
def telegram_Bot(token, chat_id, message):
    if not token or not chat_id:
        return

    url = f"{telegram_api_url}/bot{token}/sendMessage"
    data = {
        "chat_id": chat_id,
        "message_thread_id": thread_id,
        "text": message
    }

    try:
        r = requests.post(
            url,
            json=data,
            timeout=30,
            proxies=proxies,
            verify=False,            # ⭐ 关闭 SSL 校验
        )
        print("📨 Telegram 推送成功")
    except Exception as e:
        print(f"📨 Telegram 推送失败: {e}")

# =========================
# 登录函数
# =========================
def session_login(url, username, password):
    session = requests.Session(
        impersonate="chrome110",
        verify=False                # ⭐ 整个 Session 关闭 SSL 校验
    )

    try:
        session.get(
            url,
            proxies=proxies,
            timeout=30
        )
    except Exception as e:
        print(f"❌ 登录页访问失败: {e}")
        return None

    data = {
        "swapname": username,
        "swappass": password
    }

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "Chrome/125.0.0.0 Safari/537.36"
        ),
        "Origin": BASE_URL,
        "Referer": url,
    }

    try:
        response = session.post(
            url,
            data=data,
            headers=headers,
            proxies=proxies,
            timeout=60
        )

        if response.status_code == 200 and (
            "欢迎回来" in response.text or "退出登录" in response.text
        ):
            print("✅ 登录成功")
            return session

        print("❌ 登录失败")
    except Exception as e:
        print(f"❌ 登录异常: {e}")

    return None

# =========================
# 主流程
# =========================
session = session_login(login_url, username, password)

if not session:
    telegram_Bot(
        telegram_bot_token,
        chat_id,
        "❌ ArcticCloud 登录失败"
    )
    exit(1)

for name, vps_id in config.get("VPS", {}).items():
    try:
        r = session.post(
            f"{BASE_URL}/control/detail/{vps_id}/pay/",
            timeout=240,
            proxies=proxies
        )

        if (
            r.status_code == 200
            and "免费产品已经帮您续期到当前时间的最大续期时间" in r.text
        ):
            print(f"✅ {name} 续期成功")
            telegram_Bot(
                telegram_bot_token,
                chat_id,
                f"✅ {name} 已成功续期 7 天！😋\n\nArcticCloud VPS 续期提醒"
            )
        else:
            print(f"❌ {name} 续期失败，状态码 {r.status_code}")
            telegram_Bot(
                telegram_bot_token,
                chat_id,
                f"❌ {name} 续期失败！😭\n\nArcticCloud VPS 续期提醒"
            )

    except Exception as e:
        print(f"❌ {name} 请求异常: {e}")
        telegram_Bot(
            telegram_bot_token,
            chat_id,
            f"❌ {name} 续期请求异常！😭\n\nArcticCloud VPS 续期提醒"
        )