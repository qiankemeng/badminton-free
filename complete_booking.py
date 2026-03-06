"""
完整预约脚本（包含邀请功能）
"""
import requests
import json
import re

LOG_FILE = '/private/tmp/claude-501/-Users-johnson/tasks/b8iql7exx.output'
OPENID = "242050302"
NICKNAME = "孟乾轲"
PHONE = "17737525462"

def get_token():
    with open(LOG_FILE, 'r') as f:
        tokens = re.findall(r'Authorization: (Bearer [^\s]+)', f.read())
    return tokens[-1] if tokens else None

def book_with_partner(venue_name, date, site_id, start_hour, end_hour, partner_uid=None):
    """预约场地并邀请同行人"""
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
        "orderData": {
            "openid": OPENID,
            "nickname": NICKNAME,
            "phone": PHONE,
            "date": date,
            "venue_name": venue_name,
            "venue_type": "badminton",
            "site_id": site_id,
            "total_price": 0,
            "time_list": [start_hour - 8],
            "start_time": f"{start_hour:02d}:00",
            "end_time": f"{end_hour:02d}:00"
        }
    }

    # 步骤1：创建预约
    print(f"预约 {venue_name} {date} 场地{site_id} {start_hour}:00-{end_hour}:00")
    url = "https://sportmeta.hdu.edu.cn/book/client/creat_book_info"
    resp = requests.post(url, headers=headers, json=data)
    result = resp.json()

    if result.get('message') != '预约成功':
        print(f"✗ 预约失败: {result}")
        return

    # 步骤2：创建订单
    print("创建订单...")
    order_url = "https://sportmeta.hdu.edu.cn/book/client/creat_order"
    order_resp = requests.post(order_url, headers=headers, json=data)
    order_result = order_resp.json()

    if order_result.get('status') != 'success':
        print(f"✗ 创建订单失败: {order_result}")
        return

    order_num = order_result['data']['order_num']
    print(f"✓ 订单创建成功: {order_num}")

    # 步骤3：邀请同行人（如果提供）
    if partner_uid:
        print(f"邀请用户 {partner_uid}...")
        invite_data = {
            "order_num": order_num,
            "openid": OPENID,
            "proc_uid": [partner_uid]
        }
        invite_url = "https://sportmeta.hdu.edu.cn/book/client/add_playing_partner"
        invite_resp = requests.post(invite_url, headers=headers, json=invite_data)
        print(f"✓ {invite_resp.json()['message']}")

    print("\n✓ 全部完成！")

if __name__ == '__main__':
    # 示例：预约周日场地11，8-9点，邀请用户
    book_with_partner("综合馆羽毛球", "2026-3-8", 11, 8, 9, "31001804451")
