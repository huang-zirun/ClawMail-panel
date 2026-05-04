# ClawMail-panel 开发规格

## Why

用户需要在 Windows 本地运行一个独立的 Claw 邮箱网页收件箱，通过 `mail-cli` 监听多个 Claw 邮箱的新邮件，保存到本地 SQLite 数据库，并通过本地网页统一展示邮件列表和详情。当前项目仅有设计文档，尚无任何代码实现。

## What Changes

- 创建完整的项目骨架（目录结构、依赖管理、配置文件模板）
- 实现配置文件读取模块（`app/config.py`）
- 实现 SQLite 数据库初始化与操作模块（`app/database.py`）
- 实现邮件数据模型（`app/models.py`）
- 实现多账号邮件监听服务（`app/watcher.py`）
- 实现 Basic Auth 安全模块（`app/security.py`）
- 实现 FastAPI Web 应用（`app/main.py`）
- 实现邮件列表页面（`app/templates/index.html`）
- 实现邮件详情页面（`app/templates/detail.html`）
- 实现基础样式（`app/static/style.css`）
- 创建 Windows 本地启动脚本（`scripts/dev.ps1`）
- 创建配置示例文件（`config.example.json`）

## Impact

- Affected specs: 全部功能从零开始构建
- Affected code: 无既有代码，全新项目

## ADDED Requirements

### Requirement: 项目骨架

系统 SHALL 提供完整的项目目录结构，包含 `app/`、`app/templates/`、`app/static/`、`data/`、`scripts/` 等目录，以及 `pyproject.toml`（使用 uv 管理依赖）和 `config.example.json` 配置模板。依赖管理使用 uv（`uv sync` 安装依赖，`uv run python <script>` 运行脚本）。

#### Scenario: 项目初始化
- **WHEN** 用户克隆项目并执行 `uv sync`
- **THEN** 所有依赖安装成功，项目可运行

### Requirement: mail-cli 安装

系统 SHALL 依赖 `@clawemail/mail-cli`（npm 全局安装），用于监听 Claw 邮箱新邮件。安装命令为 `npm install -g @clawemail/mail-cli`。

#### Scenario: mail-cli 已安装
- **WHEN** 系统启动 watcher 时 mail-cli 已全局安装
- **THEN** 正常启动邮件监听

#### Scenario: mail-cli 未安装
- **WHEN** 系统找不到 mail-cli 命令
- **THEN** 输出错误日志提示用户执行 `npm install -g @clawemail/mail-cli`

### Requirement: 配置文件读取

系统 SHALL 从本地 JSON 配置文件读取以下信息：`enabled`（全局开关）、`accounts`（账号列表，含 profile/email/display_name）、`db_path`（数据库路径）、`basic_auth_user` 和 `basic_auth_password`。

#### Scenario: 配置文件正常读取
- **WHEN** 配置文件存在且格式正确
- **THEN** 系统正确解析所有配置项

#### Scenario: 配置文件不存在
- **WHEN** 配置文件路径无效
- **THEN** 系统输出错误日志并退出，不崩溃

#### Scenario: 配置字段缺失
- **WHEN** 配置文件中缺少必要字段
- **THEN** 系统输出明确的缺失字段提示

### Requirement: SQLite 数据库

系统 SHALL 使用 SQLite 存储邮件数据，表名 `emails`，包含字段：id、profile、account_name、mail_id、sender、recipients、cc、subject、date_text、text_body、html_body、attachments_json、header_raw、raw_json、is_read、created_at。`UNIQUE(profile, mail_id)` 约束确保同一账号同一邮件不重复写入。

#### Scenario: 数据库初始化
- **WHEN** 系统启动时数据库文件不存在
- **THEN** 自动创建数据库文件和 emails 表

#### Scenario: 邮件去重
- **WHEN** 同一 profile 和 mail_id 的邮件再次写入
- **THEN** 使用 `INSERT OR IGNORE` 静默忽略，不报错

### Requirement: 多账号邮件监听

系统 SHALL 为配置中的每个账号启动独立监听线程，运行 `mail-cli --profile <profile> mail watch --quiet`，持续读取 stdout 每行 JSON 并写入 SQLite。子进程异常退出后自动重启（延迟 5 秒）。某个账号失败不影响其他账号。

#### Scenario: 正常监听
- **WHEN** mail-cli 输出一行合法 JSON
- **THEN** 解析并写入 SQLite 数据库

#### Scenario: JSON 解析失败
- **WHEN** 某行不是合法 JSON
- **THEN** 输出错误日志，继续读取下一行，不崩溃

#### Scenario: 子进程退出
- **WHEN** mail-cli 子进程异常退出
- **THEN** 5 秒后自动重启该账号的监听

#### Scenario: mail-cli 未安装
- **WHEN** 系统找不到 mail-cli 命令
- **THEN** 输出错误日志提示用户安装

### Requirement: 邮件列表页面

系统 SHALL 在 `GET /` 提供邮件列表页面，按 `created_at` 倒序展示最近 300 封邮件，显示：账号、时间、发件人、主题、已读/未读状态。

#### Scenario: 邮件列表展示
- **WHEN** 用户访问首页
- **THEN** 显示最近 300 封邮件列表，按时间倒序排列

### Requirement: 邮件详情页面

系统 SHALL 在 `GET /mail/{id}` 提供邮件详情页面，显示：账号、发件人、收件人、抄送、主题、时间、正文、附件信息。打开详情页后自动将邮件标记为已读。HTML 邮件正文使用 `<iframe sandbox srcdoc="...">` 渲染，无 HTML 时展示纯文本。

#### Scenario: 查看邮件详情
- **WHEN** 用户点击邮件列表中的某封邮件
- **THEN** 显示邮件详情，该邮件标记为已读

#### Scenario: HTML 正文渲染
- **WHEN** 邮件包含 html_body
- **THEN** 使用 iframe sandbox 渲染 HTML 内容

#### Scenario: 纯文本正文
- **WHEN** 邮件无 html_body 但有 text_body
- **THEN** 展示纯文本正文

### Requirement: Basic Auth 登录保护

系统 SHALL 使用 HTTP Basic Auth 保护所有页面，用户名和密码从配置文件读取。

#### Scenario: 未认证访问
- **WHEN** 用户未提供认证信息访问页面
- **THEN** 返回 401 要求登录

#### Scenario: 正确认证
- **WHEN** 用户提供正确的用户名和密码
- **THEN** 允许访问页面

### Requirement: 日志记录

系统 SHALL 输出以下日志信息：服务启动、配置加载结果、启动的账号监听、watcher 启动/退出/重启、新邮件入库成功、JSON 解析失败、数据库写入失败、mail-cli stderr 输出。不打印敏感认证信息。

#### Scenario: 日志输出
- **WHEN** 系统运行过程中发生关键事件
- **THEN** 在控制台输出对应日志

### Requirement: Windows 本地启动脚本

系统 SHALL 提供 `scripts/dev.ps1` 脚本，简化本地启动流程。

#### Scenario: 一键启动
- **WHEN** 用户执行 `.\scripts\dev.ps1`
- **THEN** 自动启动 watcher 和 Web 服务

## MODIFIED Requirements

无（全新项目）

## REMOVED Requirements

无（全新项目）
