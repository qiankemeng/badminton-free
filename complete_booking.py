"""完整预约脚本（包含邀请功能）。"""
import booking_core


def book_with_partner(venue_name, date, site_id, start_hour, end_hour, partner_uid=None):
    """预约场地并邀请同行人。"""
    print(f"预约 {venue_name} {date} 场地{site_id} {start_hour}:00-{end_hour}:00")
    result = booking_core.book(venue_name, date, site_id, start_hour, end_hour, partner_uid)

    if result['success']:
        print(f"✓ 全部完成！订单号: {result['order_num']}")
    else:
        print(f"✗ {result['message']}")


if __name__ == '__main__':
    venue_name = input("场馆名 [综合馆羽毛球]: ").strip() or "综合馆羽毛球"
    date = input("日期 (例如 2026-3-14): ").strip()
    site_id = int(input("场地号: ").strip())
    start_hour = int(input("开始小时: ").strip())
    end_hour = int(input("结束小时: ").strip())
    partner_uid = input("同行人UID [可留空]: ").strip() or None
    book_with_partner(venue_name, date, site_id, start_hour, end_hour, partner_uid)
