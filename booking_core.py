"""预约核心功能"""
import base64
import json
import requests
import re
import config_manager

API_BASE = "https://sportmeta.hdu.edu.cn/book/client"
REQUEST_TIMEOUT = 10
DEFAULT_HEADERS = {
    'Content-Type': 'application/json',
    'User-Agent': 'Mozilla/5.0 (Linux; Android 15) AppleWebKit/537.36 AliApp(DingTalk/8.2.6)',
    'Origin': 'https://sportmeta.hdu.edu.cn',
    'Referer': 'https://sportmeta.hdu.edu.cn/book/dingtalk/',
    'X-Requested-With': 'com.alibaba.android.rimet'
}


def _safe_json(response):
    """尽量把响应解析为 JSON，失败时退回文本。"""
    try:
        return response.json()
    except ValueError:
        return None


def _print_response_debug(step, response, payload=None):
    """在请求失败时打印完整服务端信息，便于排查。"""
    print(f"\n[DEBUG] {step}")
    print(f"URL: {response.request.method} {response.url}")
    print(f"状态码: {response.status_code}")

    if payload is not None:
        print("请求体:")
        print(json.dumps(payload, ensure_ascii=False, indent=2))

    response_json = _safe_json(response)
    if response_json is not None:
        print("服务端返回:")
        print(json.dumps(response_json, ensure_ascii=False, indent=2))
        return

    text = response.text.strip()
    print("服务端返回:")
    print(text[:2000] if text else "<empty>")


def _post_json(step, url, headers, payload):
    """统一发送 POST 请求，并在异常时输出调试信息。"""
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=REQUEST_TIMEOUT)
        return response, None
    except requests.RequestException as exc:
        print(f"\n[DEBUG] {step}")
        print(f"请求异常: {exc}")
        print("请求体:")
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return None, str(exc)


def _decode_token_payload(token):
    """解析 JWT payload，用于识别当前 token 对应的账号。"""
    try:
        raw_token = token.split(" ", 1)[1] if token.startswith("Bearer ") else token
        parts = raw_token.split(".")
        if len(parts) != 3:
            return {}

        payload = parts[1]
        padding = "=" * (-len(payload) % 4)
        decoded = base64.urlsafe_b64decode(payload + padding)
        return json.loads(decoded.decode("utf-8"))
    except Exception:
        return {}


def _validate_identity(config, token):
    """预约前校验 token 与本地身份是否一致。"""
    payload = _decode_token_payload(token)
    token_openid = payload.get("openid")
    config_openid = str(config.get("openid", ""))

    if not token_openid or not config_openid:
        return None

    if str(token_openid) == config_openid:
        return None

    return (
        f"本地配置账号({config_openid})与当前token账号({token_openid})不一致。"
        "请重新抓取 dingtalk_login，或更新 ~/.badminton_config.json 后再预约。"
    )


def _missing_identity_fields(config):
    return [field for field in config_manager.IDENTITY_KEYS if not str(config.get(field, "")).strip()]


def _ensure_booking_identity(config, token):
    """确认预约必需的账号信息已经就绪。"""
    missing_fields = _missing_identity_fields(config)
    if missing_fields:
        return (
            "缺少预约所需的账号信息: "
            + ", ".join(missing_fields)
            + "。请先运行 mitmdump -s capture_proxy.py -p 8080，"
            + "并在钉钉中打开预约页面完成抓包。"
        )

    return _validate_identity(config, token)


def sync_identity_from_token(token=None):
    """从 JWT payload 提取 openid，与本地 config 比对并同步。

    返回 (config, synced: bool)。
    """
    if token is None:
        token = get_token()
    if not token:
        return config_manager.load(), False

    payload = _decode_token_payload(token)
    token_openid = payload.get("openid")
    if not token_openid:
        return config_manager.load(), False

    config = config_manager.load()
    if str(config.get("openid", "")) == str(token_openid):
        return config, False

    config, updated = config_manager.sync_identity({"openid": str(token_openid)})
    return config, updated


def get_headers():
    """从 headers.json 读取完整 headers，如果不存在则使用默认值"""
    headers = DEFAULT_HEADERS.copy()
    try:
        with open('headers.json') as f:
            loaded_headers = json.load(f)
            headers.update(loaded_headers)
            return headers
    except:
        return headers

def get_token():
    # 优先从 token.txt 读取
    try:
        with open('token.txt') as f:
            token = f.read().strip()
            if token:
                return token
    except:
        pass
    
    # 回退到从日志文件读取
    config = config_manager.load()
    log_file = str(config.get('log_file', '')).strip()
    if not log_file:
        return None

    try:
        with open(log_file) as f:
            tokens = re.findall(r'Authorization: (Bearer [^\s]+)', f.read())
        return tokens[-1] if tokens else None
    except:
        return None


def get_runtime_context(require_identity=False):
    """统一读取当前运行所需的 token、headers 和配置。"""
    config = config_manager.load()
    token = get_token()

    if not token:
        return None, "Token未找到，请先抓包获取最新登录信息"

    identity_error = _ensure_booking_identity(config, token) if require_identity else None
    if identity_error:
        return None, identity_error

    headers = get_headers()
    headers['Authorization'] = token

    return {
        "config": config,
        "token": token,
        "headers": headers,
    }, None


def invite_partner(order_num, partner_uid):
    """给已存在订单邀请同行人。"""
    context, error = get_runtime_context(require_identity=True)
    if error:
        return {"success": False, "message": error}

    invite_data = {
        "order_num": order_num,
        "openid": context["config"]["openid"],
        "proc_uid": [partner_uid]
    }
    invite_resp, error = _post_json(
        "邀请同行人失败",
        f"{API_BASE}/add_playing_partner",
        context["headers"],
        invite_data
    )
    if error:
        return {"success": False, "message": f"邀请同行人请求异常: {error}"}

    invite_result = _safe_json(invite_resp)
    if invite_result is None:
        _print_response_debug("邀请同行人返回非 JSON 响应", invite_resp, invite_data)
        return {"success": False, "message": "邀请同行人失败，服务端返回非 JSON 响应"}

    if invite_resp.status_code != 200:
        _print_response_debug("邀请同行人失败", invite_resp, invite_data)
        return {"success": False, "message": invite_result.get("message", "邀请同行人失败")}

    if (
        ('status' in invite_result and invite_result.get('status') != 'success')
        or ('message' in invite_result and invite_result.get('message') not in ('操作成功', '邀请成功'))
    ):
        _print_response_debug("邀请同行人失败", invite_resp, invite_data)
        return {"success": False, "message": invite_result.get("message", "邀请同行人失败")}

    return {"success": True, "message": invite_result.get("message", "邀请成功")}

def book(venue, date, site, start, end, partner=None):
    context, error = get_runtime_context(require_identity=True)
    if error:
        return {"success": False, "message": error}

    config = context["config"]
    headers = context["headers"]

    data = {
        "orderData": {
            "openid": config['openid'],
            "nickname": config['nickname'],
            "phone": config['phone'],
            "date": date,
            "venue_name": venue,
            "venue_type": "badminton",
            "site_id": site,
            "total_price": 0,
            "time_list": list(range(start - 8, end - 8)),
            "start_time": f"{start:02d}:00",
            "end_time": f"{end:02d}:00"
        }
    }

    # 创建预约
    resp, error = _post_json(
        "创建预约失败",
        f"{API_BASE}/creat_book_info",
        headers,
        data
    )
    if error:
        return {"success": False, "message": f"创建预约请求异常: {error}"}

    result = _safe_json(resp)
    if result is None:
        _print_response_debug("创建预约返回非 JSON 响应", resp, data)
        return {"success": False, "message": "创建预约失败，服务端返回非 JSON 响应"}

    if resp.status_code != 200 or result.get('message') != '预约成功':
        _print_response_debug("创建预约失败", resp, data)
        return {"success": False, "message": result.get('message', '预约失败')}

    # 创建订单
    order_resp, error = _post_json(
        "创建订单失败",
        f"{API_BASE}/creat_order",
        headers,
        data
    )
    if error:
        return {"success": False, "message": f"创建订单请求异常: {error}"}

    order_result = _safe_json(order_resp)
    if order_result is None:
        _print_response_debug("创建订单返回非 JSON 响应", order_resp, data)
        return {"success": False, "message": "订单创建失败，服务端返回非 JSON 响应"}

    if order_resp.status_code != 200 or order_result.get('status') != 'success':
        _print_response_debug("创建订单失败", order_resp, data)
        return {"success": False, "message": order_result.get('message', '订单创建失败')}

    order_num = order_result['data']['order_num']

    # 邀请同行人
    if partner:
        invite_result = invite_partner(order_num, partner)
        if not invite_result["success"]:
            print(f"✗ {invite_result['message']}")

    return {"success": True, "order_num": order_num}

def get_bookings():
    context, error = get_runtime_context(require_identity=False)
    if error:
        print(error)
        return None

    resp, error = _post_json(
        "查询预约失败",
        f"{API_BASE}/post_order_info",
        context["headers"],
        {}
    )
    if error:
        print(f"请求失败: {error}")
        return None

    result = _safe_json(resp)
    if result is None:
        _print_response_debug("查询预约返回非 JSON 响应", resp, {})
        return None

    if resp.status_code != 200:
        _print_response_debug("查询预约失败", resp, {})
        return None

    return result
