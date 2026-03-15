"""查看当前抓包得到的 token / headers / 账号信息。"""
import json
import os
from datetime import datetime

import booking_core
import config_manager


def show_status():
    token = booking_core.get_token()
    if not token:
        print("✗ 未找到 token")
        print("请先运行: mitmdump -s capture_proxy.py -p 8080")
        print("然后在钉钉中打开预约页面完成抓包。")
        return

    payload = booking_core._decode_token_payload(token)

    # 自动同步：如果 JWT 中的 openid 与本地 config 不一致，自动更新
    config, synced = booking_core.sync_identity_from_token(token)
    if synced:
        print("✓ 已自动同步 token 中的 openid 到本地配置")

    print("✓ 已读取当前 token\n")
    print(f"openid: {payload.get('openid', '<unknown>')}")

    exp = payload.get('exp')
    if exp:
        print(f"过期时间: {datetime.fromtimestamp(exp).strftime('%Y-%m-%d %H:%M:%S')}")

    print(f"headers.json: {'存在' if os.path.exists('headers.json') else '缺失'}")
    print(f"token.txt: {'存在' if os.path.exists('token.txt') else '缺失'}")
    print("当前本地账号配置:")
    print(json.dumps(
        {
            "openid": config.get("openid"),
            "nickname": config.get("nickname"),
            "phone": config.get("phone"),
        },
        ensure_ascii=False,
        indent=2,
    ))


if __name__ == '__main__':
    show_status()
