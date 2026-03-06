"""
查询我的预约
"""
import requests
import json
import re

LOG_FILE = '/private/tmp/claude-501/-Users-johnson/tasks/b8iql7exx.output'

def get_token():
    with open(LOG_FILE, 'r') as f:
        tokens = re.findall(r'Authorization: (Bearer [^\s]+)', f.read())
    return tokens[-1] if tokens else None

def get_my_bookings():
    token = get_token()
    if not token:
        print("✗ 未找到token")
        return

    headers = {
        'Authorization': token,
        'Content-Type': 'application/json',
        'User-Agent': 'Mozilla/5.0 (Linux; Android 15) AppleWebKit/537.36 AliApp(DingTalk/8.2.6)',
        'Origin': 'https://sportmeta.hdu.edu.cn',
        'Referer': 'https://sportmeta.hdu.edu.cn/book/dingtalk/',
        'X-Requested-With': 'com.alibaba.android.rimet'
    }

    url = "https://sportmeta.hdu.edu.cn/book/client/post_order_info"
    resp = requests.post(url, headers=headers, json={})
    result = resp.json()

    if 'order_info' in result:
        orders = result['order_info']
        if orders:
            print(f"✓ 共有 {len(orders)} 个预约:\n")
            for order in orders:
                print(json.dumps(order, indent=2, ensure_ascii=False))
        else:
            print("当前没有预约")
    else:
        print(json.dumps(result, indent=2, ensure_ascii=False))

if __name__ == '__main__':
    get_my_bookings()
