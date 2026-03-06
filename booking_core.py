"""预约核心功能"""
import requests
import re
import config_manager

def get_token():
    config = config_manager.load()
    try:
        with open(config['log_file']) as f:
            tokens = re.findall(r'Authorization: (Bearer [^\s]+)', f.read())
        return tokens[-1] if tokens else None
    except:
        return None

def book(venue, date, site, start, end, partner=None):
    config = config_manager.load()
    token = get_token()

    if not token:
        return {"success": False, "message": "Token未找到，请先更新token"}

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
            "openid": config['openid'],
            "nickname": config['nickname'],
            "phone": config['phone'],
            "date": date,
            "venue_name": venue,
            "venue_type": "badminton",
            "site_id": site,
            "total_price": 0,
            "time_list": [start - 8],
            "start_time": f"{start:02d}:00",
            "end_time": f"{end:02d}:00"
        }
    }

    # 创建预约
    resp = requests.post("https://sportmeta.hdu.edu.cn/book/client/creat_book_info",
                        headers=headers, json=data)
    result = resp.json()

    if result.get('message') != '预约成功':
        return {"success": False, "message": result.get('message', '预约失败')}

    # 创建订单
    order_resp = requests.post("https://sportmeta.hdu.edu.cn/book/client/creat_order",
                              headers=headers, json=data)
    order_result = order_resp.json()

    if order_result.get('status') != 'success':
        return {"success": False, "message": "订单创建失败"}

    order_num = order_result['data']['order_num']

    # 邀请同行人
    if partner:
        invite_data = {
            "order_num": order_num,
            "openid": config['openid'],
            "proc_uid": [partner]
        }
        requests.post("https://sportmeta.hdu.edu.cn/book/client/add_playing_partner",
                     headers=headers, json=invite_data)

    return {"success": True, "order_num": order_num}

def get_bookings():
    config = config_manager.load()
    token = get_token()

    if not token:
        return None

    headers = {
        'Authorization': token,
        'Content-Type': 'application/json'
    }

    resp = requests.post("https://sportmeta.hdu.edu.cn/book/client/post_order_info",
                        headers=headers, json={})
    return resp.json()
