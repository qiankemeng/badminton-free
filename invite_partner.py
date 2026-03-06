"""
邀请同行人
"""
import requests
import json
import re

LOG_FILE = '/private/tmp/claude-501/-Users-johnson/tasks/b8iql7exx.output'

def get_token():
    with open(LOG_FILE, 'r') as f:
        tokens = re.findall(r'Authorization: (Bearer [^\s]+)', f.read())
    return tokens[-1] if tokens else None

def invite_partner(order_num, uid):
    """邀请同行人"""
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

    data = {
        "order_num": order_num,
        "openid": "242050302",
        "proc_uid": [uid]
    }

    url = "https://sportmeta.hdu.edu.cn/book/client/add_playing_partner"
    resp = requests.post(url, headers=headers, json=data)
    print(json.dumps(resp.json(), indent=2, ensure_ascii=False))

if __name__ == '__main__':
    # 示例：邀请用户
    order_num = input("订单号: ")
    uid = input("被邀请人UID: ")
    invite_partner(order_num, uid)
