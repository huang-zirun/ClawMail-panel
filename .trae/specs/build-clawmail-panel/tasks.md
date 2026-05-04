# Tasks

- [x] Task 0: 安装 mail-cli（已完成：`npm install -g @clawemail/mail-cli`）

- [x] Task 1: 创建项目骨架
  - [x] SubTask 1.1: 创建 `pyproject.toml`，使用 uv 管理依赖（fastapi、uvicorn、jinja2、python-multipart）
  - [x] SubTask 1.2: 创建目录结构 `app/`、`app/templates/`、`app/static/`、`data/`、`scripts/`
  - [x] SubTask 1.3: 创建 `app/__init__.py`（空文件）
  - [x] SubTask 1.4: 创建 `data/.gitkeep`
  - [x] SubTask 1.5: 创建 `config.example.json` 配置模板

- [x] Task 2: 实现配置读取模块 `app/config.py`
  - [x] SubTask 2.1: 定义配置数据类（Account、AppConfig）
  - [x] SubTask 2.2: 实现 JSON 配置文件加载函数 `load_config(path)`
  - [x] SubTask 2.3: 处理配置文件不存在、字段缺失等错误情况

- [x] Task 3: 实现 SQLite 数据库模块 `app/database.py`
  - [x] SubTask 3.1: 实现数据库初始化函数 `init_db(db_path)`，创建 emails 表
  - [x] SubTask 3.2: 实现邮件插入函数 `insert_email(db_path, email_data)`，使用 INSERT OR IGNORE
  - [x] SubTask 3.3: 实现邮件查询函数 `get_emails(db_path, limit=300)` 和 `get_email_by_id(db_path, email_id)`
  - [x] SubTask 3.4: 实现标记已读函数 `mark_as_read(db_path, email_id)`

- [x] Task 4: 实现邮件数据模型 `app/models.py`
  - [x] SubTask 4.1: 定义 Email 数据类，字段与数据库表对应

- [x] Task 5: 实现多账号邮件监听服务 `app/watcher.py`
  - [x] SubTask 5.1: 实现单账号监听函数 `watch_account(account, db_path)`，启动 mail-cli 子进程
  - [x] SubTask 5.2: 实现 JSON 行解析与邮件入库逻辑
  - [x] SubTask 5.3: 实现子进程异常退出自动重启（延迟 5 秒）
  - [x] SubTask 5.4: 实现多账号并发监听，每个账号独立线程
  - [x] SubTask 5.5: 实现 `__main__` 入口，支持 `python -m app.watcher` 启动
  - [x] SubTask 5.6: 处理 mail-cli 未安装、JSON 解析失败、数据库写入失败等错误

- [x] Task 6: 实现 Basic Auth 安全模块 `app/security.py`
  - [x] SubTask 6.1: 实现 Basic Auth 校验函数，从配置读取用户名密码
  - [x] SubTask 6.2: 实现 FastAPI 依赖项，保护所有路由

- [x] Task 7: 实现 FastAPI Web 应用 `app/main.py`
  - [x] SubTask 7.1: 创建 FastAPI 应用实例，挂载静态文件和模板
  - [x] SubTask 7.2: 实现 `GET /` 邮件列表路由
  - [x] SubTask 7.3: 实现 `GET /mail/{id}` 邮件详情路由（含标记已读）
  - [x] SubTask 7.4: 集成 Basic Auth 中间件

- [x] Task 8: 实现邮件列表页面 `app/templates/index.html`
  - [x] SubTask 8.1: 邮件列表表格，显示账号、时间、发件人、主题、已读/未读状态
  - [x] SubTask 8.2: 点击邮件跳转到详情页

- [x] Task 9: 实现邮件详情页面 `app/templates/detail.html`
  - [x] SubTask 9.1: 显示邮件完整信息（账号、发件人、收件人、抄送、主题、时间）
  - [x] SubTask 9.2: HTML 正文使用 `<iframe sandbox srcdoc="...">` 渲染
  - [x] SubTask 9.3: 无 HTML 时展示纯文本正文
  - [x] SubTask 9.4: 展示附件信息列表

- [x] Task 10: 实现基础样式 `app/static/style.css`
  - [x] SubTask 10.1: 邮件列表和详情页的基础 CSS 样式

- [x] Task 11: 创建 Windows 本地启动脚本 `scripts/dev.ps1`
  - [x] SubTask 11.1: 脚本自动启动 watcher 和 Web 服务

- [x] Task 12: 错误处理与日志完善
  - [x] SubTask 12.1: 为所有模块添加 logging 日志输出
  - [x] SubTask 12.2: 确保错误不导致程序崩溃，仅输出日志

# Task Dependencies

- Task 2 依赖 Task 1（需要项目骨架）
- Task 3 依赖 Task 1（需要项目骨架）
- Task 4 依赖 Task 1（需要项目骨架）
- Task 5 依赖 Task 2、Task 3、Task 4（需要配置、数据库、模型）
- Task 6 依赖 Task 2（需要配置中的认证信息）
- Task 7 依赖 Task 2、Task 3、Task 6（需要配置、数据库、安全模块）
- Task 8 依赖 Task 7（需要路由）
- Task 9 依赖 Task 7（需要路由）
- Task 10 依赖 Task 8、Task 9（需要页面）
- Task 11 依赖 Task 5、Task 7（需要 watcher 和 web 服务）
- Task 12 依赖所有其他 Task（最后完善）
