"""邀请同行人"""
import booking_core


def main():
    order_num = input("订单号: ").strip()
    uid = input("被邀请人UID: ").strip()

    result = booking_core.invite_partner(order_num, uid)
    if result["success"]:
        print(f"✓ {result['message']}")
    else:
        print(f"✗ {result['message']}")


if __name__ == '__main__':
    main()
