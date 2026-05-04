# ClawMail-panel

一个独立部署的 ClawMail 邮箱网页收件箱。通过 `mail-cli` 监听多个 Claw 邮箱的新邮件，保存到本地 SQLite 数据库，并通过本地网页统一展示邮件列表和正文内容，无需接入 Claw Agent。

## 功能特性

- **多账号监听**：同时监听多个 Claw 邮箱账号的新邮件，每个账号独立线程，互不影响
- **本地持久化**：邮件自动写入 SQLite 数据库，服务重启后不丢失
- **邮件去重**：基于 `profile + mail_id` 唯一约束，自动防止重复写入
- **网页收件箱**：本地 FastAPI 服务提供邮件列表和详情查看
- **已读/未读状态**：打开邮件详情后自动标记为已读
- **安全渲染**：HTML 邮件通过 iframe sandbox 隔离渲染，防止 XSS
- **Basic Auth**：单用户密码保护，本地场景够用
- **自动重连**：mail-cli 监听进程异常退出后自动重启

## 技术栈

| 层面 | 选型 |
|------|------|
| 语言 | Python 3.10+ |
| Web 框架 | FastAPI |
| 数据库 | SQLite |
| 模板引擎 | Jinja2 |
| 邮件监听 | mail-cli |
| 包管理 | uv |

## 环境要求

- Windows 操作系统
- Python >= 3.10
- [uv](https://docs.astral.sh/uv/) 包管理器
- [mail-cli](https://claw.163.com) 已安装并配置好 profile

## 快速开始

### 1. 克隆项目并安装依赖

```powershell
uv sync
```

### 2. 配置邮箱账号

复制配置文件模板：

```powershell
copy config.example.json config.json
```

编辑 `config.json`，填入你的 Claw 邮箱账号信息：

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

> **注意**：每个账号的 `profile` 必须已在 mail-cli 中登录。可使用 `mail-cli --profile <name> auth test` 验证登录状态。

### 3. 启动服务

使用开发脚本一键启动（同时启动邮件监听和 Web 服务）：

```powershell
.\scripts\dev.ps1
```

或分别手动启动：

```powershell
# 终端 1：启动邮件监听
uv run python -m app.watcher

# 终端 2：启动 Web 服务
uv run uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

### 4. 访问收件箱

打开浏览器访问 http://127.0.0.1:8000，使用配置文件中设置的 Basic Auth 用户名和密码登录。

## 项目结构

```
claw-mail-panel/
  app/
    __init__.py
    main.py           # FastAPI Web 服务
    config.py         # 配置读取
    database.py       # SQLite 数据库操作
    watcher.py        # 邮件监听服务
    models.py         # 数据模型
    security.py       # 安全相关
    templates/
      index.html      # 邮件列表页
      detail.html     # 邮件详情页
    static/
      style.css       # 样式文件
  data/
    emails.db         # SQLite 数据库（运行时生成）
  scripts/
    dev.ps1           # 开发启动脚本
  config.json         # 配置文件（需自行创建）
  config.example.json # 配置模板
  pyproject.toml      # 项目依赖
```

## 数据库设计

SQLite 单表 `emails`：

```sql
CREATE TABLE emails (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  profile TEXT NOT NULL,          -- mail-cli profile 名称
  account_name TEXT,              -- 账号显示名称
  mail_id TEXT NOT NULL,          -- 邮件唯一 ID
  sender TEXT,                    -- 发件人
  recipients TEXT,                -- 收件人
  cc TEXT,                        -- 抄送
  subject TEXT,                   -- 主题
  date_text TEXT,                 -- 邮件日期
  text_body TEXT,                 -- 纯文本正文
  html_body TEXT,                 -- HTML 正文
  attachments_json TEXT,          -- 附件列表 JSON
  header_raw TEXT,                -- 原始邮件头
  raw_json TEXT,                  -- 原始 JSON 数据
  is_read INTEGER DEFAULT 0,      -- 是否已读
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  UNIQUE(profile, mail_id)        -- 防止重复
);
```

## Web 路由

| 路由 | 说明 |
|------|------|
| `GET /` | 邮件列表（按时间倒序，最近 300 封） |
| `GET /mail/{id}` | 邮件详情（打开后自动标记已读） |

## 配置说明

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `enabled` | boolean | 是 | 是否启用监听 |
| `accounts` | array | 是 | 邮箱账号列表 |
| `accounts[].profile` | string | 是 | mail-cli profile 名称 |
| `accounts[].email` | string | 是 | 邮箱地址 |
| `accounts[].display_name` | string | 是 | 显示名称 |
| `db_path` | string | 是 | SQLite 数据库路径 |
| `basic_auth_user` | string | 是 | 登录用户名 |
| `basic_auth_password` | string | 是 | 登录密码 |

## 注意事项

- 本项目仅设计用于 **Windows 本地运行**，不涉及 Docker / Nginx / HTTPS / 服务器部署
- 邮件监听依赖 `mail-cli`，请确保已正确安装并登录
- 附件仅展示信息，暂不支持下载
- 暂不支持邮件搜索、回复、删除、归档等功能

## 相关文档

- [Mail-CLI 操作指南](./Mail-CLI操作指南.md) — mail-cli 完整命令参考
- [journey/design.md](./journey/design.md) — 项目设计快照与架构决策
