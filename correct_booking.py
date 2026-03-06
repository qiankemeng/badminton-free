"""
正确的预约脚本
"""
import requests
import json
import re

LOG_FILE = '/private/tmp/claude-501/-Users-johnson/tasks/b8iql7exx.output'
PHONE = "17737525462"
OPENID = "242050302"
NICKNAME = "孟乾轲"

def get_token():
    with open(LOG_FILE, 'r') as f:
        tokens = re.findall(r'Authorization: (Bearer [^\s]+)', f.read())
    return tokens[-1] if tokens else None

def book(venue_name, date, site_id, start_hour, end_hour):
    """预约场地"""
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

    # 计算time_list (时段编号，从0开始)
    time_list = [start_hour - 8]  # 假设8点是时段0

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
            "time_list": time_list,
            "start_time": f"{start_hour:02d}:00",
            "end_time": f"{end_hour:02d}:00"
        }
    }

    url = "https://sportmeta.hdu.edu.cn/book/client/creat_book_info"
    resp = requests.post(url, headers=headers, json=data)
    print(json.dumps(resp.json(), indent=2, ensure_ascii=False))

if __name__ == '__main__':
    # 预约场地7，周日9-10点
    book("综合馆羽毛球", "2026-3-8", 7, 9, 10)
