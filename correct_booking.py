"""最小预约脚本。"""
import booking_core


def book(venue_name, date, site_id, start_hour, end_hour):
    """预约场地。"""
    result = booking_core.book(venue_name, date, site_id, start_hour, end_hour)
    if result['success']:
        print(f"✓ 预约成功！订单号: {result['order_num']}")
    else:
        print(f"✗ {result['message']}")


if __name__ == '__main__':
    venue_name = input("场馆名 [综合馆羽毛球]: ").strip() or "综合馆羽毛球"
    date = input("日期 (例如 2026-3-14): ").strip()
    site_id = int(input("场地号: ").strip())
    start_hour = int(input("开始小时: ").strip())
    end_hour = int(input("结束小时: ").strip())
    book(venue_name, date, site_id, start_hour, end_hour)
