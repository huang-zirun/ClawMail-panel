# ClawMail-panel 验收清单

## 环境准备
- [x] mail-cli 已全局安装（`npm install -g @clawemail/mail-cli`）
- [x] `mail-cli --help` 可正常执行

## 项目骨架
- [ ] `pyproject.toml` 存在且包含 fastapi、uvicorn、jinja2 依赖
- [ ] 目录结构完整：`app/`、`app/templates/`、`app/static/`、`data/`、`scripts/`
- [ ] `config.example.json` 包含完整配置模板

## 配置读取
- [ ] `app/config.py` 能正确加载 JSON 配置文件
- [ ] 配置文件不存在时输出错误日志并退出
- [ ] 配置字段缺失时输出明确提示

## 数据库
- [ ] `app/database.py` 能自动创建 SQLite 数据库和 emails 表
- [ ] emails 表包含所有必要字段且 UNIQUE(profile, mail_id) 约束生效
- [ ] INSERT OR IGNORE 正确防止重复邮件写入
- [ ] 邮件查询按 created_at 倒序返回最近 300 封
- [ ] 标记已读功能正常工作

## 邮件监听
- [ ] `app/watcher.py` 能为每个账号启动独立监听线程
- [ ] 正确运行 `mail-cli --profile <profile> mail watch --quiet`
- [ ] 能解析每行 JSON 并写入数据库
- [ ] 子进程异常退出后 5 秒自动重启
- [ ] 某个账号失败不影响其他账号
- [ ] mail-cli 未安装时输出错误提示
- [ ] JSON 解析失败时输出日志继续运行
- [ ] 支持 `python -m app.watcher` 启动

## Web 页面
- [ ] `GET /` 显示邮件列表，包含账号、时间、发件人、主题、已读/未读
- [ ] `GET /mail/{id}` 显示邮件详情
- [ ] 打开邮件详情后自动标记为已读
- [ ] HTML 邮件正文使用 `<iframe sandbox srcdoc="...">` 渲染
- [ ] 无 HTML 时展示纯文本正文
- [ ] 附件信息正确展示

## 安全
- [ ] 所有页面受 Basic Auth 保护
- [ ] 未认证访问返回 401
- [ ] 正确的用户名密码可以访问

## 日志
- [ ] 服务启动时输出日志
- [ ] 配置加载结果有日志
- [ ] 每个账号 watcher 启动/退出/重启有日志
- [ ] 新邮件入库成功有日志
- [ ] JSON 解析失败有日志
- [ ] 不打印敏感认证信息

## 本地运行
- [ ] `scripts/dev.ps1` 能一键启动 watcher 和 Web 服务
- [ ] 浏览器访问 `http://127.0.0.1:8000` 可正常使用
- [ ] 服务重启后不重复插入同一封邮件

## 整体验收
- [ ] 可在 Windows 本地启动
- [ ] 可配置两个 Claw 邮箱账号
- [ ] 两账号收到新邮件后均自动写入 SQLite
- [ ] 网页列表能显示不同账号的邮件
- [ ] 点击邮件可查看详情
- [ ] 邮件详情能显示 HTML 或纯文本正文
- [ ] 打开邮件详情后标记为已读
- [ ] 不需要接入 Claw Agent
- [ ] 不需要服务器部署
