# 杭电羽毛球场地自动预约

自动预约杭州电子科技大学体育场馆的羽毛球场地，支持定时抢场和同行人邀请。

## 功能特性

- 🎯 自动预约指定场地和时段
- ⏰ 定时任务（每晚8点自动抢后天场地）
- 👥 支持邀请同行人
- 📱 基于钉钉认证的API调用

## 仓库说明

仓库只保留源码和示例文件，不提交真实登录态。运行时会在本地生成：

- `token.txt`：最新 Bearer token
- `headers.json`：抓包得到的请求头
- `~/.badminton_config.json`：当前账号信息和默认预约参数

其中 `headers.example.json` 仅用于展示格式，不会被程序直接读取。

## 快速开始

### 1. 安装依赖

```bash
pip install requests schedule mitmproxy
```

### 2. 首次配置

```bash
# 先抓包一次，自动保存 token、headers 和账号信息
mitmdump -s capture_proxy.py -p 8080

# 手机配置代理后，在钉钉中打开预约页面
# 抓包完成后，账号信息会自动写入 ~/.badminton_config.json
```

### 3. 检查登录状态

```bash
python3 update_token.py
```

会显示当前 token 对应的 `openid`、过期时间，以及本地配置是否已同步。

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

无需再手动修改脚本中的个人信息。抓包后会自动保存到本地：

```python
token.txt        # 最新 Bearer token
headers.json     # 最新请求 headers
~/.badminton_config.json  # openid / nickname / phone / 默认预约参数
```

你仍然可以在 `badminton.py` 的“设置”菜单里调整默认场馆、场地号、时段和同行人 UID。

## Token管理

Token有效期约2小时，需要定期刷新：

1. 启动抓包服务器
2. 手机操作一次（打开预约页面即可）
3. 运行 `python3 update_token.py` 检查当前 token 和账号状态
4. 关闭抓包服务器

```bash
# 启动
mitmdump -s capture_proxy.py -p 8080

# 关闭
pkill -f mitmdump
```

## 定时抢场

```bash
python3 auto_grab.py
```

默认只注册每天 `20:00` 的定时任务，不会启动就立即下单。若你确实要马上执行一次：

```bash
python3 auto_grab.py --run-now
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

- ⚠️ `token.txt` 和 `headers.json` 是本地运行态文件，不要提交到 GitHub
- ⚠️ Token每2小时过期，需定期更新
- ⚠️ 系统每晚8点开放后天场地预约
- ⚠️ 仅供学习交流使用，请遵守学校规定

## License

MIT
