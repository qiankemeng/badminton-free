"""
更新Token - 从抓包日志提取最新token
"""
import re

LOG_FILE = '/private/tmp/claude-501/-Users-johnson/tasks/b8iql7exx.output'

def get_latest_token():
    """提取最新token"""
    try:
        with open(LOG_FILE, 'r') as f:
            content = f.read()

        tokens = re.findall(r'Authorization: (Bearer [^\s]+)', content)

        if tokens:
            latest = tokens[-1]
            print(f"✓ 找到最新token")
            print(f"\nToken: {latest}\n")

            # 保存到文件
            with open('current_token.txt', 'w') as f:
                f.write(latest)
            print("✓ 已保存到 current_token.txt")
            return latest
        else:
            print("✗ 未找到token")
            print("请在手机钉钉中操作一下（打开球场预定页面）")
            return None
    except Exception as e:
        print(f"✗ 错误: {e}")
        return None

if __name__ == '__main__':
    print("正在提取最新token...\n")
    get_latest_token()
