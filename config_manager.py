"""配置管理"""
import json
import os

CONFIG_FILE = os.path.expanduser("~/.badminton_config.json")

DEFAULT_CONFIG = {
    "openid": "242050302",
    "nickname": "孟乾轲",
    "phone": "17737525462",
    "log_file": "/private/tmp/claude-501/-Users-johnson/tasks/b8iql7exx.output",
    "venue": "综合馆羽毛球",
    "site": 8,
    "start_time": 8,
    "end_time": 9,
    "partner_uid": ""
}

def load():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE) as f:
            return json.load(f)
    return DEFAULT_CONFIG.copy()

def save(config):
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
