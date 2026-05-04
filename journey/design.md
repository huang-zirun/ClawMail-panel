# ClawMail-panel 设计快照

> 本文档是项目的权威参考。每次 agent 会话开始时应首先阅读此文件。
> 当对项目的理解发生实质性变化时，应更新此文件。

## 项目名称

`claw-mail-panel`

## 项目目标

在 Windows 本地运行一个独立的 Claw 邮箱网页收件箱。通过 `mail-cli` 监听多个 Claw 邮箱的新邮件，保存到本地 SQLite 数据库，并通过本地网页展示邮件列表和详情。

**核心定位**：本地轻量邮件查看面板——能监听、能保存、能展示、能区分账号、不重复写入。

## 第一版范围

- 仅本地运行，不部署到服务器
- 不需要 Docker / Nginx / HTTPS / 域名
- 不接入 Claw Agent，仅通过 `mail-cli` 读取邮箱数据
- 单用户 Basic Auth 保护

## 技术栈

| 层面 | 选型 | 理由 |
|------|------|------|
| 语言 | Python 3 | 本地脚本场景，生态成熟 |
| Web 框架 | FastAPI | 异步支持好，自带 API 文档，轻量 |
| 数据库 | SQLite | 零配置本地存储，无需额外服务 |
| 模板 | Jinja2 | Python 标准模板引擎，服务端渲染 |
| 邮件监听 | mail-cli | 官方 CLI 工具，支持 `mail watch` NDJSON 流 |

**不使用**：Docker、Nginx、HTTPS、前端框架、多用户系统、云服务器部署。

## 核心架构

系统分为两个独立部分：

### 1. 邮件监听服务（watcher）

- 读取配置文件，为每个账号启动独立监听线程
- 每个线程运行 `mail-cli --profile <profile> mail watch --quiet`
- 持续读取 stdout，每行按 JSON 解析
- 写入 SQLite，使用 `INSERT OR IGNORE` 防止重复
- 子进程异常退出后自动重启
- 某个账号失败不影响其他账号

### 2. 本地 Web 页面

- FastAPI 提供服务，监听 `127.0.0.1:8000`
- Basic Auth 登录保护
- 路由：
  - `GET /` — 邮件列表（按 `created_at` 倒序，最近 300 封）
  - `GET /mail/{id}` — 邮件详情（打开后标记已读）

## 数据库设计

SQLite，单表 `emails`：

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

`UNIQUE(profile, mail_id)` 确保同一账号同一邮件不重复写入。

## 配置文件格式

```json
{
  "enabled": true,
  "accounts": [
    {
      "profile": "mail1",
      "email": "first@claw.163.com",
      "display_name": "邮箱一"
    }
  ],
  "db_path": "./data/emails.db",
  "basic_auth_user": "admin",
  "basic_auth_password": "change-this-password"
}
```

## 目录结构

```
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

## 关键设计决策

1. **不接入 Claw Agent** — 仅用 `mail-cli` 读取数据，降低耦合
2. **每账号独立线程** — 隔离故障，单账号崩溃不影响全局
3. **INSERT OR IGNORE 去重** — 利用 UNIQUE 约束，简洁可靠
4. **iframe sandbox 渲染 HTML 邮件** — 防止 XSS，安全隔离
5. **Basic Auth** — 本地场景够用，无需复杂认证体系
6. **服务端渲染（Jinja2）** — 第一版不需要前端框架，简单直接

## 第一版必须实现

- 本地配置文件读取
- 多账号配置与监听
- 邮件入库与去重
- 邮件列表页 / 详情页
- 已读 / 未读状态
- Basic Auth
- Windows 本地运行说明
- README

## 第一版不实现

- 服务器部署 / Docker / Nginx / HTTPS
- 附件下载（仅展示附件信息）
- 回复 / 删除 / 归档邮件
- 搜索功能
- 多用户权限
- 邮件转发
- 通知推送（Telegram / 企业微信）
- 自动发现子邮箱
- 邮箱管理（clawemail create/list/delete）

## 实现优先级

1. 项目骨架 → 2. 配置读取 → 3. SQLite 初始化 → 4. 单账号 watcher → 5. 多账号 watcher → 6. 邮件入库去重 → 7. 邮件列表页 → 8. 邮件详情页 → 9. Basic Auth → 10. Windows 本地运行脚本 → 11. README → 12. 错误处理与日志完善

## 错误处理要求

需覆盖：配置文件缺失、字段缺失、mail-cli 未安装、profile 未登录、watch 启动失败、JSON 解析失败、数据库写入失败、监听断开。错误输出到控制台日志，不导致程序崩溃。

## 验收标准

1. Windows 本地可启动
2. 可配置两个 Claw 邮箱账号
3. 两账号收到新邮件后均自动写入 SQLite
4. 网页列表能显示不同账号的邮件
5. 点击邮件可查看详情
6. 邮件详情能显示 HTML 或纯文本正文
7. 打开邮件详情后标记为已读
8. 服务重启后不重复插入同一封邮件
9. 不需要接入 Claw Agent
10. 不需要服务器部署
11. README 能指导用户在本地跑起来
