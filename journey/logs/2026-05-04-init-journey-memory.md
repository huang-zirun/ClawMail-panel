# 2026-05-04 初始化 Journey 记忆系统

## 操作内容

根据 `AGENTS.md` 中的 Journey memory 规范，为项目创建了 `journey/` 目录结构。

## 创建的文件

| 文件 | 用途 |
|------|------|
| `journey/design.md` | 项目权威设计快照，基于根目录 `design.md` 整理 |
| `journey/logs/.gitkeep` | 过程日志目录 |
| `journey/research/.gitkeep` | 研究笔记目录 |
| `journey/plans/.gitkeep` | 计划文档目录 |

## design.md 内容来源

从根目录已有的 `design.md` 迁移并扩展，补充了：

- 技术选型理由表格
- 6 项关键设计决策（独立线程隔离、INSERT OR IGNORE 去重、iframe sandbox 渲染 HTML 邮件、Basic Auth、Jinja2 服务端渲染、不接入 Claw Agent）
- 结构化的验收标准

## 备注

- 根目录的 `design.md` 保留未动，`journey/design.md` 是 agent 会话的权威参考
- 三个子目录（logs / research / plans）目前仅含 `.gitkeep`，后续随项目推进逐步填充
