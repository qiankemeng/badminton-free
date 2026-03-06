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

### 2. 首次配置

```bash
# 启动程序
python3 badminton.py

# 进入设置菜单配置个人信息
```

### 3. 获取Token

首次使用需要抓取token：

```bash
# 在程序中选择"3. 更新Token"
# 或手动执行：
mitmdump -s capture_proxy.py -p 8080

# 手机配置代理（电脑IP:8080）
# 访问 http://mitm.it 安装证书
# 在钉钉中打开预约页面
# Ctrl+C 停止抓包
```

### 4. 开始使用

```bash
python3 badminton.py
```

**主要功能：**
- 立即预约：交互式输入预约信息
- 查看预约：查询当前所有预约
- 更新Token：重新抓取认证token
- 设置：配置默认参数

## 核心文件说明

| 文件 | 功能 |
|------|------|
| `badminton.py` | 主程序（交互式终端界面） |
| `booking_core.py` | 预约核心逻辑 |
| `config_manager.py` | 配置管理 |
| `capture_proxy.py` | mitmproxy抓包脚本 |
| `auto_grab.py` | 定时抢场脚本（高级） |

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
