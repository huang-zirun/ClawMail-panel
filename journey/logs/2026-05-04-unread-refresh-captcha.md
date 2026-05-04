# 2026-05-04 已读状态实时刷新 + 验证码提取

## 问题
点击邮件进入详情页后，`mark_as_read` 已更新数据库，但返回列表页时浏览器缓存旧页面，未读标记（粗体+红色"未读"）不刷新，必须按 F5。

## 方案
采用 AJAX + 右侧滑出详情面板：
- 列表页通过 `fetch('/api/emails')` 加载 JSON 渲染表格
- 点击邮件行 → 右侧滑出面板，同时 `POST /api/emails/{id}/read` 标记已读
- 列表行实时移除 `unread` 类，状态文本变为"已读"
- 新增验证码提取，列表行和详情面板均可一键复制

## 变更文件
- `app/captcha.py` — 新增验证码正则提取模块
- `app/main.py` — 新增 `/api/emails`、`/api/emails/{id}`、`/api/emails/{id}/read` 路由；保留 `/mail/{id}` 兼容
- `app/templates/index.html` — 重写为 SPA，支持 AJAX 加载和右侧面板
- `app/static/style.css` — 新增面板、验证码标签、复制按钮样式

## 验证
`uv run python -c "import app.main"` 成功，无导入错误。
