#!/usr/bin/env python3
"""杭电羽毛球场地自动预约"""
import os
import sys
import time
import random
from datetime import datetime, timedelta
import config_manager
import booking_core
import update_token

def first_run_check():
    """首次运行检测：缺少 token 或身份信息时给出引导提示。"""
    token = booking_core.get_token()
    config = config_manager.load()
    openid = str(config.get("openid", "")).strip()

    if not token or not openid:
        print("="*40)
        print("  首次使用指引")
        print("="*40)
        if not token:
            print("✗ 未找到 token.txt")
        if not openid:
            print("✗ 未找到账号信息 (openid)")
        print()
        print("请先完成抓包以获取登录凭证：")
        print("  1. 运行: mitmdump -s capture_proxy.py -p 8080")
        print("  2. 手机设置 HTTP 代理指向本机 8080 端口")
        print("  3. 在钉钉中打开体育场馆预约页面")
        print("  4. 抓包完成后按 Ctrl+C 停止")
        print()
        print("也可在主菜单中选择「更新Token」完成此步骤。")
        print()
        return False
    return True


def menu():
    print("\n" + "="*40)
    print("  杭电羽毛球场地自动预约")
    print("="*40)
    print("1. 立即预约")
    print("2. 定时预约（精确到毫秒）")
    print("3. 候补预约（多场地轮换）")
    print("4. 查看预约")
    print("5. 更新Token")
    print("6. 设置")
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

def scheduled_book():
    config = config_manager.load()
    print("\n--- 定时预约（精确到毫秒）---")
    
    default_date = (datetime.now() + timedelta(days=2)).strftime("%Y-%-m-%-d")
    
    date = input(f"日期 [{default_date}]: ") or default_date
    site = int(input(f"场地号 [{config['site']}]: ") or config['site'])
    start = int(input(f"开始 [{config['start_time']}]: ") or config['start_time'])
    end = int(input(f"结束 [{config['end_time']}]: ") or config['end_time'])
    partner = input(f"同行人UID [{config['partner_uid']}]: ") or config['partner_uid']
    
    print("\n输入发送时间（格式：HH:MM:SS.mmm）")
    print("例如：20:00:00.000 表示晚上8点整")
    target_time = input("发送时间: ")
    
    try:
        target_dt = datetime.strptime(target_time, "%H:%M:%S.%f")
        now = datetime.now()
        target = now.replace(hour=target_dt.hour, minute=target_dt.minute, 
                           second=target_dt.second, microsecond=target_dt.microsecond)
        
        if target < now:
            target += timedelta(days=1)
        
        wait_seconds = (target - datetime.now()).total_seconds()
        
        print(f"\n预约配置：")
        print(f"  场地：{config['venue']} {date} 场地{site} {start}:00-{end}:00")
        print(f"  发送时间：{target.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]}")
        print(f"  等待时间：{wait_seconds:.3f}秒")
        
        confirm = input("\n确认开始倒计时？(y/n): ")
        if confirm.lower() != 'y':
            print("已取消")
            return
        
        print(f"\n倒计时开始...")
        while True:
            now = datetime.now()
            remaining = (target - now).total_seconds()
            
            if remaining <= 0:
                break
            
            if remaining > 60:
                print(f"\r剩余 {int(remaining//60)}分{int(remaining%60)}秒    ", end='', flush=True)
                time.sleep(1)
            elif remaining > 1:
                print(f"\r剩余 {remaining:.3f}秒    ", end='', flush=True)
                time.sleep(0.1)
            else:
                print(f"\r剩余 {remaining:.3f}秒    ", end='', flush=True)
                time.sleep(0.001)
        
        print("\n\n🚀 发送预约请求...")
        result = booking_core.book(config['venue'], date, site, start, end,
                                   partner if partner else None)
        
        if result['success']:
            print(f"✓ 预约成功！订单号: {result['order_num']}")
        else:
            print(f"✗ {result['message']}")
            
    except ValueError:
        print("✗ 时间格式错误，请使用 HH:MM:SS.mmm 格式")

def backup_book():
    config = config_manager.load()
    print("\n--- 候补预约（多场地轮换）---")
    
    default_date = (datetime.now() + timedelta(days=2)).strftime("%Y-%-m-%-d")
    date = input(f"日期 [{default_date}]: ") or default_date
    
    print("\n输入候补场地（逗号分隔，如：1,2,3）")
    sites_input = input(f"场地号列表: ")
    sites = [int(s.strip()) for s in sites_input.split(',')]
    
    start = int(input(f"开始时间 [{config['start_time']}]: ") or config['start_time'])
    end = int(input(f"结束时间 [{config['end_time']}]: ") or config['end_time'])
    partner = input(f"同行人UID [{config['partner_uid']}]: ") or config['partner_uid']
    
    print("\n输入发送时间（格式：HH:MM:SS.mmm）")
    target_time = input("发送时间: ")
    
    try:
        target_dt = datetime.strptime(target_time, "%H:%M:%S.%f")
        now = datetime.now()
        target = now.replace(hour=target_dt.hour, minute=target_dt.minute, 
                           second=target_dt.second, microsecond=target_dt.microsecond)
        
        if target < now:
            target += timedelta(days=1)
        
        print(f"\n候补场地：{sites}")
        print(f"发送时间：{target.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]}")
        
        confirm = input("\n确认开始倒计时？(y/n): ")
        if confirm.lower() != 'y':
            print("已取消")
            return
        
        print(f"\n倒计时开始...")
        while True:
            now = datetime.now()
            remaining = (target - now).total_seconds()
            
            if remaining <= 0:
                break
            
            if remaining > 60:
                print(f"\r剩余 {int(remaining//60)}分{int(remaining%60)}秒    ", end='', flush=True)
                time.sleep(1)
            elif remaining > 1:
                print(f"\r剩余 {remaining:.3f}秒    ", end='', flush=True)
                time.sleep(0.1)
            else:
                print(f"\r剩余 {remaining:.3f}秒    ", end='', flush=True)
                time.sleep(0.001)
        
        print("\n\n🚀 开始候补预约...")
        for i, site in enumerate(sites):
            print(f"\n尝试场地 {site}...")
            result = booking_core.book(config['venue'], date, site, start, end,
                                       partner if partner else None)
            
            if result['success']:
                print(f"✓ 预约成功！场地{site} 订单号: {result['order_num']}")
                break
            else:
                print(f"✗ 场地{site}失败: {result['message']}")
                if i < len(sites) - 1:
                    delay = random.uniform(0.1, 0.3)
                    print(f"等待 {delay:.3f}秒后尝试下一个...")
                    time.sleep(delay)
        else:
            print("\n✗ 所有候补场地都预约失败")
            
    except ValueError:
        print("✗ 时间格式错误，请使用 HH:MM:SS.mmm 格式")

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

def do_update_token():
    print("\n--- 更新Token ---")
    print("1. 启动抓包: mitmdump -s capture_proxy.py -p 8080")
    print("2. 手机设置代理并访问预约页面")
    print("3. 停止抓包: Ctrl+C")

    choice = input("\n启动抓包？(y/n): ")
    if choice.lower() == 'y':
        os.system("mitmdump -s capture_proxy.py -p 8080")
        # 抓包完成后自动展示最新状态
        print()
        update_token.show_status()

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
    first_run_check()

    while True:
        menu()
        choice = input("\n选择: ")

        if choice == '1':
            quick_book()
        elif choice == '2':
            scheduled_book()
        elif choice == '3':
            backup_book()
        elif choice == '4':
            view_bookings()
        elif choice == '5':
            do_update_token()
        elif choice == '6':
            settings()
        elif choice == '0':
            break

        input("\n按回车继续...")

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n再见！")
