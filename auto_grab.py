"""定时抢场地脚本。"""
import sys
import time
from datetime import datetime, timedelta

import schedule

import booking_core
import config_manager

def book_venue():
    """执行预约"""
    config = config_manager.load()
    # 计算后天日期
    target_date = (datetime.now() + timedelta(days=2)).strftime("%Y-%-m-%-d")

    print(f"\n{'='*50}")
    print(f"开始预约: {datetime.now()}")
    print(
        f"目标: {config['venue']} {target_date} "
        f"场地{config['site']} {config['start_time']}-{config['end_time']}"
    )
    print(f"{'='*50}\n")

    result = booking_core.book(
        config['venue'],
        target_date,
        config['site'],
        config['start_time'],
        config['end_time'],
        config['partner_uid'] or None,
    )
    if result['success']:
        print(f"\n✓ 预约成功！订单号: {result['order_num']}")
        return True

    print(f"\n✗ 预约失败: {result['message']}")
    return False

def job():
    """定时任务"""
    book_venue()

if __name__ == '__main__':
    config = config_manager.load()
    print("定时抢场地脚本已启动")
    print(
        f"配置: {config['venue']} 场地{config['site']} "
        f"{config['start_time']}-{config['end_time']}"
    )
    print("每天20:00自动执行\n")

    # 设置定时任务
    schedule.every().day.at("20:00").do(job)

    if "--run-now" in sys.argv:
        print("立即执行一次...")
        book_venue()

    print("\n等待定时任务...")
    while True:
        schedule.run_pending()
        time.sleep(1)
