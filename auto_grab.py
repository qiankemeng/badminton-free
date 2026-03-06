"""
定时抢场地脚本
每天晚8点自动预约后天的场地
"""
import requests
import json
import re
import time
from datetime import datetime, timedelta
import schedule

# 配置
PHONE = "17737525462"
LOG_FILE = '/private/tmp/claude-501/-Users-johnson/tasks/b8iql7exx.output'

# 预约配置
VENUE_NAME = "综合馆羽毛球"
VENUE_TYPE = "羽毛球"
TARGET_SITE = 8  # 场地号
START_TIME = 8   # 开始时段
END_TIME = 9     # 结束时段

def get_token():
    """从抓包日志获取最新token"""
    try:
        with open(LOG_FILE, 'r') as f:
            content = f.read()
        tokens = re.findall(r'Authorization: (Bearer [^\s]+)', content)
        return tokens[-1] if tokens else None
    except:
        return None

def book_venue():
    """执行预约"""
    # 计算后天日期
    target_date = (datetime.now() + timedelta(days=2)).strftime("%Y-%-m-%-d")

    print(f"\n{'='*50}")
    print(f"开始预约: {datetime.now()}")
    print(f"目标: {VENUE_NAME} {target_date} 场地{TARGET_SITE} {START_TIME}-{END_TIME}")
    print(f"{'='*50}\n")

    token = get_token()
    if not token:
        print("✗ 未找到token")
        return False

    headers = {
        'Authorization': token,
        'Content-Type': 'application/json',
        'User-Agent': 'Mozilla/5.0 (Linux; Android 15) AppleWebKit/537.36 AliApp(DingTalk/8.2.6)',
        'Origin': 'https://sportmeta.hdu.edu.cn',
        'Referer': 'https://sportmeta.hdu.edu.cn/book/dingtalk/',
        'X-Requested-With': 'com.alibaba.android.rimet'
    }

    # 预约数据（使用正确的格式）
    time_list = [START_TIME - 8]  # 时段编号从0开始，8点是0

    data = {
        "orderData": {
            "openid": "242050302",
            "nickname": "孟乾轲",
            "phone": PHONE,
            "date": target_date,
            "venue_name": VENUE_NAME,
            "venue_type": "badminton",
            "site_id": TARGET_SITE,
            "total_price": 0,
            "time_list": time_list,
            "start_time": f"{START_TIME:02d}:00",
            "end_time": f"{END_TIME:02d}:00"
        }
    }

    url = "https://sportmeta.hdu.edu.cn/book/client/creat_book_info"

    try:
        resp = requests.post(url, headers=headers, json=data, timeout=10)
        result = resp.json()
        print(json.dumps(result, indent=2, ensure_ascii=False))

        if result.get('status') == 'success':
            print("\n✓ 预约成功！")
            return True
        else:
            print(f"\n✗ 预约失败: {result.get('message')}")
            return False
    except Exception as e:
        print(f"\n✗ 请求失败: {e}")
        return False

def job():
    """定时任务"""
    book_venue()

if __name__ == '__main__':
    print("定时抢场地脚本已启动")
    print(f"配置: {VENUE_NAME} 场地{TARGET_SITE} {START_TIME}-{END_TIME}")
    print("每天20:00自动执行\n")

    # 设置定时任务
    schedule.every().day.at("20:00").do(job)

    # 测试模式：立即执行一次
    print("测试模式：立即执行一次...")
    book_venue()

    print("\n等待定时任务...")
    while True:
        schedule.run_pending()
        time.sleep(1)
