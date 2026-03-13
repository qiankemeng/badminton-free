"""
抓包脚本 - 用于捕获钉钉球场预定的API请求
运行: mitmdump -s capture_proxy.py
"""
from mitmproxy import http
import json
import config_manager

class CaptureBooking:
    def __init__(self):
        self.target_domain = "sportmeta.hdu.edu.cn"
        self.token_file = "token.txt"
        self.headers_file = "headers.json"
        self.login_path = "/book/client/dingtalk_login"
        self.header_whitelist = {
            "accept",
            "accept-encoding",
            "accept-language",
            "content-type",
            "origin",
            "referer",
            "sec-fetch-dest",
            "sec-fetch-mode",
            "sec-fetch-site",
            "user-agent",
            "x-requested-with",
        }

    def _save_token(self, token, source):
        with open(self.token_file, "w") as f:
            f.write(token)
        print(f"✓ Token已保存到 {self.token_file} ({source})")

    def _sync_config(self, login_data):
        _, updated = config_manager.sync_identity(login_data)
        if updated:
            print("✓ 已同步登录账号信息到 ~/.badminton_config.json")

    def response(self, flow: http.HTTPFlow) -> None:
        if self.target_domain in flow.request.pretty_url:
            print("\n" + "="*80)
            print(f"[请求] {flow.request.method} {flow.request.pretty_url}")
            print(f"[Headers]")

            response_json = None
            saved_token = False
            if flow.response.content:
                try:
                    response_json = json.loads(flow.response.content)
                except Exception:
                    response_json = None

            headers_dict = {
                key: value
                for key, value in flow.request.headers.items()
                if key.lower() in self.header_whitelist
            }

            # dingtalk_login 返回的 data.token 才是最新可用 token
            if self.login_path in flow.request.pretty_url and response_json:
                login_data = response_json.get("data", {})
                response_token = login_data.get("token")
                if response_token:
                    bearer_token = (
                        response_token
                        if response_token.startswith("Bearer ")
                        else f"Bearer {response_token}"
                    )
                    self._save_token(bearer_token, "来自登录响应")
                    self._sync_config(login_data)
                    saved_token = True

            # 非登录接口时，退回保存请求头里的 Authorization
            auth_token = flow.request.headers.get("Authorization", "")
            if not saved_token and auth_token:
                self._save_token(auth_token, "来自请求头")

            # 保存完整 headers
            with open(self.headers_file, "w") as f:
                json.dump(headers_dict, f, ensure_ascii=False, indent=2)
            print(f"✓ Headers已保存到 {self.headers_file}")
            
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
                if response_json is not None:
                    print(f"[Response] {json.dumps(response_json, ensure_ascii=False, indent=2)}")
                else:
                    print(f"[Response] {flow.response.content.decode('utf-8', errors='ignore')[:500]}")
            print("="*80)

addons = [CaptureBooking()]
