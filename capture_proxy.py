"""
抓包脚本 - 用于捕获钉钉球场预定的API请求
运行: mitmdump -s capture_proxy.py
"""
from mitmproxy import http
import json

class CaptureBooking:
    def __init__(self):
        self.target_domain = "sportmeta.hdu.edu.cn"

    def response(self, flow: http.HTTPFlow) -> None:
        if self.target_domain in flow.request.pretty_url:
            print("\n" + "="*80)
            print(f"[请求] {flow.request.method} {flow.request.pretty_url}")
            print(f"[Headers]")
            for k, v in flow.request.headers.items():
                print(f"  {k}: {v}")

            if flow.request.content:
                try:
                    body = json.loads(flow.request.content)
                    print(f"[Body] {json.dumps(body, ensure_ascii=False, indent=2)}")
                except:
                    print(f"[Body] {flow.request.content.decode('utf-8', errors='ignore')}")

            print(f"\n[响应] Status: {flow.response.status_code}")
            if flow.response.content:
                try:
                    resp = json.loads(flow.response.content)
                    print(f"[Response] {json.dumps(resp, ensure_ascii=False, indent=2)}")
                except:
                    print(f"[Response] {flow.response.content.decode('utf-8', errors='ignore')[:500]}")
            print("="*80)

addons = [CaptureBooking()]
