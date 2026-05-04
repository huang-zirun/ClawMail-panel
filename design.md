# AGENTS.md

## 项目名称

`claw-mail-panel`

## 项目目标

本项目第一版只实现本地运行版本。

用户希望在 Windows 本地环境中运行一个独立的 Claw 邮箱网页收件箱。系统通过 `mail-cli` 监听一个或多个 Claw 邮箱的新邮件，把收到的邮件保存到本地 SQLite 数据库，并通过本地网页展示邮件列表和邮件详情。

本项目第一版不需要部署到服务器，不需要 Docker，不需要 Nginx，不需要 HTTPS。

本项目不接入 Claw Agent，不让 Claw Agent 参与邮件处理，只通过 `mail-cli` 读取邮箱数据。

## 第一版目标效果

用户在 Windows 本地启动项目后，可以打开浏览器访问：

```text
http://127.0.0.1:8000
```

页面中可以看到多个 Claw 邮箱收到的新邮件，并能查看每封邮件的详情。

## 输入

用户提供一个本地配置文件，例如：

```json
{
  "enabled": true,
  "accounts": [
    {
      "profile": "mail1",
      "email": "first@claw.163.com",
      "display_name": "邮箱一"
    },
    {
      "profile": "mail2",
      "email": "second@claw.163.com",
      "display_name": "邮箱二"
    }
  ],
  "db_path": "./data/emails.db",
  "basic_auth_user": "admin",
  "basic_auth_password": "change-this-password"
}
```

其中：

- `profile` 是本地 `mail-cli` 的 profile 名称。
- `email` 是邮箱地址，仅用于标识和说明。
- `display_name` 是页面中展示的账号名称。
- `db_path` 是本地 SQLite 数据库路径。
- `basic_auth_user` 和 `basic_auth_password` 用于保护本地页面。

## 输出

系统输出一个本地网页收件箱。

页面需要展示：

- 邮件所属账号
- 发件人
- 收件人
- 邮件标题
- 邮件时间
- 邮件正文
- 已读 / 未读状态
- 附件信息，第一版只保存和展示附件信息，不实现附件下载

## 技术栈

第一版使用：

- Python 3
- FastAPI
- SQLite
- Jinja2
- `mail-cli`

不使用：

- Docker
- Nginx
- HTTPS
- 前端框架
- 多用户系统
- 云服务器部署

## 核心设计

系统分为两个部分：

### 1. 邮件监听服务

后台服务读取配置文件，为每个账号启动一个独立监听进程：

```bash
mail-cli --profile <profile> mail watch --quiet
```

程序持续读取 `mail-cli` 输出的每一行 JSON，把新邮件写入 SQLite。

每个账号独立监听，某个账号失败不应影响其他账号。

### 2. 本地 Web 页面

FastAPI 提供本地网页。

至少包含：

```text
GET /
GET /mail/{id}
```

页面功能：

- 邮件列表
- 邮件详情
- 已读 / 未读
- 按账号区分邮件来源
- Basic Auth 登录保护

## 推荐目录结构

```text
claw-mail-panel/
  AGENTS.md
  README.md
  requirements.txt
  config.example.json

  app/
    __init__.py
    main.py
    config.py
    database.py
    watcher.py
    models.py
    security.py

    templates/
      index.html
      detail.html

    static/
      style.css

  data/
    .gitkeep

  scripts/
    dev.ps1
```

## 本地运行方式

用户需要先安装：

- Python 3
- Node.js
- mail-cli

然后在 Windows PowerShell 中执行：

```powershell
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
```

登录邮箱 profile：

```powershell
mail-cli --profile mail1 auth login --user first@claw.163.com
mail-cli --profile mail2 auth login --user second@claw.163.com

mail-cli --profile mail1 auth test
mail-cli --profile mail2 auth test
```

启动邮件监听：

```powershell
python -m app.watcher
```

另开一个 PowerShell，启动 Web 服务：

```powershell
.\.venv\Scripts\activate
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

浏览器访问：

```text
http://127.0.0.1:8000
```

也可以提供一个 `scripts/dev.ps1`，用于简化本地启动流程。

## 数据库设计

使用 SQLite。

表名：`emails`

```sql
CREATE TABLE IF NOT EXISTS emails (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  profile TEXT NOT NULL,
  account_name TEXT,
  mail_id TEXT NOT NULL,
  sender TEXT,
  recipients TEXT,
  cc TEXT,
  subject TEXT,
  date_text TEXT,
  text_body TEXT,
  html_body TEXT,
  attachments_json TEXT,
  header_raw TEXT,
  raw_json TEXT,
  is_read INTEGER DEFAULT 0,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  UNIQUE(profile, mail_id)
);
```

必须使用：

```sql
UNIQUE(profile, mail_id)
```

用于避免重复写入同一封邮件。

## 邮件监听要求

监听服务需要做到：

1. 读取配置文件。
2. 支持多个账号。
3. 每个账号使用独立 `mail-cli profile`。
4. 每个账号启动独立 `mail watch --quiet`。
5. 持续读取 stdout。
6. 每行按 JSON 解析。
7. 写入 SQLite。
8. 使用 `INSERT OR IGNORE` 防止重复邮件。
9. 子进程异常退出后自动重启。
10. 某个账号失败不影响其他账号。

伪代码：

```python
for account in config.accounts:
    start_thread(watch_account, account)

def watch_account(account):
    while True:
        proc = subprocess.Popen([
            "mail-cli",
            "--profile",
            account.profile,
            "mail",
            "watch",
            "--quiet"
        ])

        for line in proc.stdout:
            data = json.loads(line)
            save_email(account, data)

        sleep(5)
```

## Web 页面要求

### 邮件列表页

路径：

```text
GET /
```

展示：

- 账号
- 时间
- 发件人
- 主题
- 已读 / 未读状态

默认按 `created_at` 倒序展示最近 300 封邮件。

### 邮件详情页

路径：

```text
GET /mail/{id}
```

展示：

- 账号
- 发件人
- 收件人
- 抄送
- 主题
- 时间
- 正文
- 附件信息

打开详情页后，将邮件标记为已读。

HTML 邮件正文不要直接插入主页面，应使用：

```html
<iframe sandbox srcdoc="..."></iframe>
```

如果没有 HTML 正文，则展示纯文本正文。

## 登录保护

第一版使用 Basic Auth。

配置项：

```json
{
  "basic_auth_user": "admin",
  "basic_auth_password": "change-this-password"
}
```

即使只是本地页面，也需要登录保护，避免误暴露。

## 第一版必须实现

- 本地配置文件读取
- 多账号配置
- 多账号邮件监听
- 邮件入库
- 邮件去重
- 邮件列表页
- 邮件详情页
- 已读 / 未读
- Basic Auth
- Windows 本地运行说明
- README

## 第一版不实现

- 服务器部署
- Docker
- Nginx
- HTTPS
- 域名
- 附件下载
- 回复邮件
- 删除邮件
- 归档邮件
- 搜索
- 多用户权限
- 邮件转发
- Telegram / 企业微信通知
- 自动发现子邮箱
- `clawemail create/list/delete` 等邮箱管理功能

## 附件处理

第一版只保存 `mail watch` 输出中的 `attachments` 字段，并在详情页中展示附件信息。

不实现附件下载。

后续版本再考虑通过 `mail-cli read structure` 和 `mail-cli read attachment` 下载附件。

## 错误处理要求

需要处理：

- 配置文件不存在
- 配置字段缺失
- `mail-cli` 未安装
- profile 未登录
- `mail watch` 启动失败
- 输出不是合法 JSON
- 数据库写入失败
- 某个账号监听断开

错误应输出到控制台日志，但不应导致整个程序崩溃。

## 日志要求

日志至少包含：

- 服务启动
- 配置加载结果
- 启动了哪些账号监听
- 每个账号 watcher 启动
- watcher 退出和重启
- 新邮件入库成功
- JSON 解析失败
- 数据库写入失败
- `mail-cli` stderr 输出

不要打印敏感认证信息。

## README 要求

README 需要包含：

1. 项目介绍
2. 功能列表
3. 环境要求
4. Windows 本地安装步骤
5. `mail-cli` 登录说明
6. 多账号配置说明
7. 启动 watcher
8. 启动 Web 服务
9. 浏览器访问方式
10. 常见问题
11. 安全注意事项

## 验收标准

第一版完成后，应满足：

1. 可以在 Windows 本地启动。
2. 可以配置两个 Claw 邮箱账号。
3. 两个账号收到新邮件后，系统都能自动写入 SQLite。
4. 网页列表能显示不同账号的邮件。
5. 点击邮件可以查看详情。
6. 邮件详情能显示 HTML 或纯文本正文。
7. 打开邮件详情后，该邮件变为已读。
8. 服务重启后不会重复插入同一封邮件。
9. 不需要接入 Claw Agent。
10. 不需要服务器部署。
11. README 能指导用户在本地跑起来。

## 实现优先级

按以下顺序实现：

1. 项目骨架
2. 配置读取
3. SQLite 初始化
4. 单账号 watcher
5. 多账号 watcher
6. 邮件入库去重
7. 邮件列表页
8. 邮件详情页
9. Basic Auth
10. Windows 本地运行脚本
11. README
12. 错误处理与日志完善

## 项目边界

第一版只是一个本地轻量邮件查看面板。

重点是：

- 能监听
- 能保存
- 能展示
- 能区分账号
- 不重复写入
- 本地 Windows 可运行

不要在第一版做过度设计。

<br />

<br />

