"""配置管理"""
import json
import os

CONFIG_FILE = os.path.expanduser("~/.badminton_config.json")
IDENTITY_KEYS = ("openid", "nickname", "phone")

DEFAULT_CONFIG = {
    "openid": "",
    "nickname": "",
    "phone": "",
    "log_file": "",
    "venue": "综合馆羽毛球",
    "site": 8,
    "start_time": 8,
    "end_time": 9,
    "partner_uid": ""
}

def load():
    config = DEFAULT_CONFIG.copy()
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE) as f:
            config.update(json.load(f))
    return config

def save(config):
    merged = DEFAULT_CONFIG.copy()
    merged.update(config)
    with open(CONFIG_FILE, 'w') as f:
        json.dump(merged, f, indent=2, ensure_ascii=False)


def sync_identity(identity):
    """同步当前登录账号信息到本地配置。"""
    config = load()
    updated = False

    for key in IDENTITY_KEYS:
        value = identity.get(key)
        if value and config.get(key) != value:
            config[key] = value
            updated = True

    if updated or not os.path.exists(CONFIG_FILE):
        save(config)

    return config, updated
