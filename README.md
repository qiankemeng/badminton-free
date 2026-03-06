# 杭电羽毛球场地自动预约

自动预约杭州电子科技大学体育场馆的羽毛球场地，支持定时抢场和同行人邀请。

## 功能特性

- 🎯 自动预约指定场地和时段
- ⏰ 定时任务（每晚8点自动抢后天场地）
- 👥 支持邀请同行人
- 📱 基于钉钉认证的API调用

## 快速开始

### 1. 安装依赖

```bash
pip install requests schedule mitmproxy
```

### 2. 配置抓包

首先需要获取认证token：

**手机端抓包（推荐）：**

```bash
# 启动抓包服务器
mitmdump -s capture_proxy.py -p 8080

# 手机配置代理：
# - 代理地址：你的电脑IP
# - 端口：8080
# - 安装mitmproxy证书：http://mitm.it

# 在钉钉中打开场馆预约页面，操作一次即可抓取token
```

### 3. 使用脚本

**手动预约：**

```python
python complete_booking.py
```

编辑脚本修改预约参数：
```python
book_with_partner("综合馆羽毛球", "2026-3-8", 11, 8, 9, "31001804451")
# 参数：场馆名称、日期、场地号、开始时间、结束时间、同行人UID（可选）
```

**定时自动抢场：**

```python
python auto_grab.py
```

编辑脚本配置：
```python
VENUE_NAME = "综合馆羽毛球"
TARGET_SITE = 8      # 场地号
START_TIME = 8       # 开始时段
END_TIME = 9         # 结束时段
```

## 核心文件说明

| 文件 | 功能 |
|------|------|
| `complete_booking.py` | 完整预约流程（含邀请同行人） |
| `auto_grab.py` | 定时抢场脚本（每晚8点执行） |
| `capture_proxy.py` | mitmproxy抓包脚本 |
| `update_token.py` | 更新token工具 |
| `my_bookings.py` | 查询当前预约 |

## 配置说明

修改脚本中的个人信息：

```python
OPENID = "你的openid"
NICKNAME = "你的昵称"
PHONE = "你的手机号"
LOG_FILE = "抓包日志路径"
```

## Token管理

Token有效期约2小时，需要定期更新：

1. 启动抓包服务器
2. 手机操作一次（打开预约页面即可）
3. 运行 `python update_token.py` 更新token
4. 关闭抓包服务器

```bash
# 启动
mitmdump -s capture_proxy.py -p 8080

# 关闭
pkill -f mitmdump
```

## API接口

| 接口 | 功能 |
|------|------|
| `/book/client/post_site_situation` | 查询场地可用情况 |
| `/book/client/creat_book_info` | 创建预约 |
| `/book/client/creat_order` | 创建订单 |
| `/book/client/add_playing_partner` | 邀请同行人 |
| `/book/client/post_order_info` | 查询我的预约 |

## 注意事项

- ⚠️ Token每2小时过期，需定期更新
- ⚠️ 系统每晚8点开放后天场地预约
- ⚠️ 仅供学习交流使用，请遵守学校规定

## License

MIT
