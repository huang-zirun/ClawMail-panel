# 2026-05-04 安装 mail-cli 并创建开发规格

## 操作内容

1. 全局安装 `@clawemail/mail-cli`（npm 包），用于监听 Claw 邮箱新邮件
2. 创建 ClawMail-panel 项目的开发规格文档（spec.md、tasks.md、checklist.md）

## mail-cli 安装

- 包名：`@clawemail/mail-cli`
- 安装命令：`npm install -g @clawemail/mail-cli`
- 版本：0.2.4
- 验证：`mail-cli --help` 输出正常，支持 auth、folder、mail、compose、read、clawemail 等命令

## 开发规格文档

三份文档位于 `.trae/specs/build-clawmail-panel/`：

| 文件 | 用途 |
|------|------|
| `spec.md` | 完整开发规格，10 大需求，每个需求含成功和异常场景 |
| `tasks.md` | 13 个有序任务（含 Task 0 安装 mail-cli），按实现优先级排列 |
| `checklist.md` | 39 项验收清单，覆盖环境、骨架、配置、数据库、监听、Web、安全、日志、本地运行 |

## 关键发现

- mail-cli 的 npm 包名是 `@clawemail/mail-cli`，不是 `mail-cli`（后者是另一个不相关的 SMTP 工具）
- mail-cli `mail watch --quiet` 输出 NDJSON 格式，每行一个 JSON 对象，包含 id/from/to/cc/bcc/subject/date/priority/text/html/attachments/headerRaw 字段
- 断线重连策略：1s → 2s → 4s → 8s → 16s，超过 5 次退出并返回非零状态码
