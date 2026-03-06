#!/usr/bin/env python3
"""杭电羽毛球场地自动预约"""
import os
import sys
from datetime import datetime, timedelta
import config_manager
import booking_core

def menu():
    print("\n" + "="*40)
    print("  杭电羽毛球场地自动预约")
    print("="*40)
    print("1. 立即预约")
    print("2. 查看预约")
    print("3. 更新Token")
    print("4. 设置")
    print("0. 退出")
    print("="*40)

def quick_book():
    config = config_manager.load()
    print("\n--- 立即预约 ---")

    default_date = (datetime.now() + timedelta(days=2)).strftime("%Y-%-m-%-d")

    date = input(f"日期 [{default_date}]: ") or default_date
    site = int(input(f"场地号 [{config['site']}]: ") or config['site'])
    start = int(input(f"开始 [{config['start_time']}]: ") or config['start_time'])
    end = int(input(f"结束 [{config['end_time']}]: ") or config['end_time'])
    partner = input(f"同行人UID [{config['partner_uid']}]: ") or config['partner_uid']

    print(f"\n预约 {config['venue']} {date} 场地{site} {start}:00-{end}:00")

    result = booking_core.book(config['venue'], date, site, start, end,
                               partner if partner else None)

    if result['success']:
        print(f"✓ 预约成功！订单号: {result['order_num']}")
    else:
        print(f"✗ {result['message']}")

def view_bookings():
    print("\n--- 我的预约 ---")
    result = booking_core.get_bookings()

    if not result:
        print("✗ 获取失败，请更新token")
        return

    orders = result.get('order_info', [])
    if not orders:
        print("暂无预约")
        return

    for order in orders:
        print(f"\n订单: {order['order_num']}")
        print(f"场地: {order['venue_name']} 场地{order['site_id']}")
        print(f"时间: {order['date']} {order['start_time']}-{order['end_time']}")

def update_token():
    print("\n--- 更新Token ---")
    print("1. 启动抓包: mitmdump -s capture_proxy.py -p 8080")
    print("2. 手机设置代理并访问预约页面")
    print("3. 停止抓包: Ctrl+C")

    choice = input("\n启动抓包？(y/n): ")
    if choice.lower() == 'y':
        os.system("mitmdump -s capture_proxy.py -p 8080")

def settings():
    config = config_manager.load()
    print("\n--- 设置 ---")
    print(f"1. 手机号: {config['phone']}")
    print(f"2. 场馆: {config['venue']}")
    print(f"3. 默认场地: {config['site']}")
    print(f"4. 默认时段: {config['start_time']}-{config['end_time']}")
    print(f"5. 同行人: {config['partner_uid']}")

    choice = input("\n修改 (1-5/0返回): ")

    if choice == '1':
        config['phone'] = input("手机号: ")
    elif choice == '2':
        config['venue'] = input("场馆: ")
    elif choice == '3':
        config['site'] = int(input("场地号: "))
    elif choice == '4':
        config['start_time'] = int(input("开始: "))
        config['end_time'] = int(input("结束: "))
    elif choice == '5':
        config['partner_uid'] = input("UID: ")

    if choice in '12345':
        config_manager.save(config)
        print("✓ 已保存")

def main():
    while True:
        menu()
        choice = input("\n选择: ")

        if choice == '1':
            quick_book()
        elif choice == '2':
            view_bookings()
        elif choice == '3':
            update_token()
        elif choice == '4':
            settings()
        elif choice == '0':
            break

        input("\n按回车继续...")

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n再见！")
