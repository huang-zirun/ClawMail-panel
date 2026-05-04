# 计划：创建 Journey 记忆系统

## 背景

根据 `AGENTS.md` 中的 Journey memory 规范，需要为 ClawMail-panel 项目建立 `journey/` 目录结构，作为跨 agent 会话的共享项目记忆。

项目当前状态：仅有 `AGENTS.md`、`README.md`、`design.md`、`Mail-CLI操作指南.md` 四个文件，尚无代码实现，也无 `journey/` 目录。

## 需要创建的文件和目录

### 1. `journey/design.md` — 项目设计快照

从根目录已有的 `design.md` 迁移并扩展，作为项目的权威设计文档。内容应包含：

- 项目名称与目标
- 第一版范围（本地运行、不部署）
- 技术栈（Python 3 / FastAPI / SQLite / Jinja2 / mail-cli）
- 核心架构（邮件监听服务 + 本地 Web 页面）
- 数据库设计（emails 表结构）
- 目录结构
- 关键设计决策与约束
- 不实现的功能清单

### 2. `journey/logs/` — 过程日志目录

创建目录并放置 `.gitkeep` 以确保目录被 Git 追踪。

### 3. `journey/research/` — 研究笔记目录

创建目录并放置 `.gitkeep`。

### 4. `journey/plans/` — 计划文档目录

创建目录并放置 `.gitkeep`。

## 实施步骤

1. **创建 `journey/` 目录结构**
   - 创建 `journey/logs/`、`journey/research/`、`journey/plans/` 三个子目录
   - 每个子目录放置 `.gitkeep` 文件

2. **创建 `journey/design.md`**
   - 基于根目录 `design.md` 的内容，整理为结构化的设计快照
   - 补充关键设计决策、约束、技术选型理由
   - 确保作为 agent 会话的首要参考文档

3. **验证目录结构完整性**
   - 确认所有文件和目录已正确创建

## 最终目录结构

```
journey/
  design.md          # 项目设计快照（权威参考）
  logs/
    .gitkeep
  research/
    .gitkeep
  plans/
    .gitkeep
```
