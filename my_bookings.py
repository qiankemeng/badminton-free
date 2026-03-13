"""查询我的预约"""
import json

import booking_core


def get_my_bookings():
    result = booking_core.get_bookings()
    if not result:
        print("✗ 获取失败，请先确认 token 和 headers 已抓取")
        return

    orders = result.get('order_info', [])
    if orders:
        print(f"✓ 共有 {len(orders)} 个预约:\n")
        for order in orders:
            print(json.dumps(order, indent=2, ensure_ascii=False))
    else:
        print("当前没有预约")


if __name__ == '__main__':
    get_my_bookings()
