# 计划：已读状态实时刷新 + 验证码提取一键复制

## 问题分析

当前点击邮件后，后端 `mark_as_read` 已更新数据库，但返回列表页时浏览器缓存了旧页面，未读标记（粗体 + 红色"未读"）不会自动刷新，必须按 F5 强制刷新。

## 方案选型

采用 **AJAX + 右侧滑出详情面板** 方案：
- 列表页不再整页跳转到 `/mail/{id}`
- 点击邮件行 → 右侧滑出详情面板，同时通过 API 标记已读
- 列表行实时移除 `unread` 类和未读标记
- 在列表行内直接显示提取到的验证码（如有），提供一键复制

## 实施步骤

### 1. 后端 API 调整
- `GET /api/emails` — 返回邮件列表 JSON（复用现有 `get_emails`）
- `GET /api/emails/{id}` — 返回单封邮件详情 JSON（复用现有 `get_email_by_id`）
- `POST /api/emails/{id}/read` — 标记已读，返回成功状态（复用现有 `mark_as_read`）
- 保留原有页面路由 `/` 和 `/mail/{id}` 作为兼容（或直接改造 `/` 为 SPA 入口）

### 2. 验证码提取逻辑
- 新增 `app/captcha.py`：提供 `extract_captcha(text: str) -> str | None`
- 正则规则：
  - 匹配 4-8 位连续数字
  - 或匹配 "验证码[:：]\\s*([A-Za-z0-9]{4,8})"、"code[:：]\\s*([A-Za-z0-9]{4,8})" 等常见格式
  - 优先从 `subject` 提取，其次 `text_body`，最后 `html_body`（去标签后）
- 在 `GET /api/emails` 返回的数据中，每个邮件对象增加 `captcha` 字段

### 3. 前端改造（index.html 变为 SPA 入口）
- 列表页 `/` 改为加载邮件列表 JSON 渲染表格
- 点击邮件行：
  1. 调用 `POST /api/emails/{id}/read` 标记已读
  2. 该行实时移除 `unread` 类、`status-unread` 类，文本变为"已读"
  3. 右侧滑出详情面板，通过 `GET /api/emails/{id}` 加载内容
- 详情面板内容：
  - 邮件头信息（账号、发件人、收件人、主题、时间）
  - 正文（HTML 用 iframe sandbox，纯文本用 pre）
  - 附件列表
  - 如果有验证码，面板顶部高亮显示并提供"复制"按钮
- 列表行内：
  - 如果有验证码，在主题旁显示验证码和"复制"按钮
  - 点击复制按钮直接写入剪贴板（`navigator.clipboard.writeText`）

### 4. 样式调整（style.css）
- 新增 `.detail-panel` 右侧固定面板样式（`position: fixed; right: 0; top: 0; width: 50%;` 等）
- 新增 `.captcha-badge` 验证码标签样式
- 新增 `.copy-btn` 复制按钮样式
- 调整列表页布局：详情面板滑出时列表区域缩窄或保持原样（面板覆盖）

### 5. 路由兼容
- 原有 `/mail/{id}` 页面路由保留但简化，或直接重定向到 `/` 并自动打开对应邮件面板
- 确保直接访问 `/mail/{id}` 仍能正常工作（书签兼容）

### 6. 测试验证
- 点击未读邮件 → 列表行立即变为已读样式
- 右侧面板正确显示邮件详情
- 验证码正确提取并在列表行和详情面板显示
- 复制按钮成功写入剪贴板
- 直接访问 `/mail/{id}` 正常

## 文件变更清单

| 文件 | 操作 |
|------|------|
| `app/main.py` | 新增 3 个 API 路由，调整 `/` 和 `/mail/{id}` |
| `app/captcha.py` | 新增验证码提取模块 |
| `app/templates/index.html` | 重写为 SPA，增加 JS 交互 |
| `app/templates/detail.html` | 可选保留或废弃 |
| `app/static/style.css` | 新增面板、验证码、复制按钮样式 |
| `app/database.py` | 无需修改（已有 `mark_as_read`） |

## 风险与回退

- 若前端 JS 加载失败，页面无法显示邮件列表。保留服务端渲染回退：当 JS 禁用时，原有表格链接仍可点击跳转 `/mail/{id}`。
- 验证码正则可能误匹配。提供配置项或保守规则，优先保证不误杀。
