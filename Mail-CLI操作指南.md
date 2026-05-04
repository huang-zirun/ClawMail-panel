

Mail-CLI 操作指南

概览
功能概览环境要求快速上手（Claw Agent）全局选项命令与 Claude 集成（mail watch + Claude）
概览
一个用于操作claw.163.com邮件的命令行工具

功能概览
Agent 邮箱管理 -- 通过 Open API 创建、列出、删除、启用/禁用 Claw Agent 邮箱
文件夹管理 -- 列出邮箱文件夹
邮件列表 -- 列出、搜索、获取邮件
邮件操作 -- 在文件夹间移动邮件、标记已读/未读
邮件阅读与解析 -- 查看邮件正文（纯文本/HTML）、邮件头、MIME 结构
附件处理 -- 按 Part ID 下载单个附件
写信与发送 -- 支持附件、抄送/密送、优先级
输出格式 -- 默认人类可读的表格格式，--json 用于脚本处理
环境要求
Node.js >= 18
npm 或 pnpm
快速上手（Claw Agent）
# 1. 设置 API Key
mail-cli auth apikey set ck_live_xxxxxxxxxxxxxxxx

# 2. 登录你的 Claw 主账户
mail-cli auth login --user myagent@claw.163.com

# 3. 列出已有邮箱
mail-cli clawemail list

# 4. 创建子邮箱
mail-cli clawemail create --prefix bot1 --type sub --display-name "My Bot"

# 5. 使用子邮箱
mail-cli --profile bot1 mail list --fid 1
mail-cli --profile bot1 compose send --to user@163.com --subject "Hi" --body "Hello from bot"
全局选项
--profile <name> 指定使用的配置名称（默认使用配置文件中 "default" 的值）
--json 以 JSON 格式输出结果
--verbose 显示详细的协议交互信息
--config <path> 指定自定义配置文件路径
命令
auth apikey -- API Key 管理
Claw Agent 邮箱操作需要 API Key。Key 存储在系统钥匙串（macOS Keychain / Windows 凭据管理器）中，并通过 config.json 引用。

# 保存 API Key（写入钥匙串 + 设置 config.apikeyRef）
mail-cli auth apikey set <key>

# 移除 API Key（从钥匙串删除 + 清除 config.apikeyRef）
mail-cli auth apikey remove
设置后，所有 clawemail 命令和 Claw 邮箱操作将自动使用该 Key。

auth -- 认证
# 登录当前配置（Ajax/OAuth）
mail-cli auth login
mail-cli auth login --user someone@claw.163.com

# 登出
mail-cli auth logout

# 测试认证状态
mail-cli auth test
clawemail -- Agent 邮箱管理
通过 Open API 管理 Claw Agent 邮箱。需要先设置 API Key（参见 auth apikey set）。

# 列出工作区内所有邮箱
mail-cli clawemail list
mail-cli clawemail list --json

# 创建子邮箱
mail-cli clawemail create --prefix bot1 --type sub --display-name "My Bot"

# 查看邮箱详情
mail-cli clawemail info
mail-cli clawemail info --uid myagent.bot1@claw.163.com

# 查看或更新 Agent 资料
mail-cli clawemail profile
mail-cli clawemail profile --uid myagent.bot1@claw.163.com
mail-cli clawemail profile --uid myagent.bot1@claw.163.com --display-name "New Name"

# 启用 / 禁用邮箱
mail-cli clawemail enable --uid myagent.bot1@claw.163.com
mail-cli clawemail disable --uid myagent.bot1@claw.163.com

# 删除子邮箱（主邮箱不可删除）
mail-cli clawemail delete --uid myagent.bot1@claw.163.com
clawemail create 选项：

选项	说明
--prefix <prefix>	邮箱前缀，1-64 个字符
--type <type>	邮箱类型：primary（主邮箱）或 sub（子邮箱）
--display-name <name>	Agent 显示名称
创建成功后，会自动在配置文件中添加新的 profile，并显示授权码（请妥善保存，仅显示一次）。

--uid 参数：未指定时默认使用当前配置的 user 值。

folder -- 文件夹操作
# 列出所有文件夹
mail-cli folder list
mail-cli folder list --json
mail -- 邮件操作
# 列出文件夹中的邮件
mail-cli mail list --fid 1
mail-cli mail list --fid INBOX --limit 20 --desc
mail-cli mail list --fid 1 --unread --order date

# 获取指定邮件
mail-cli mail get --ids "msg1,msg2"
mail-cli mail get --ids "msg1" --fid INBOX # IMAP 账户需要 --fid

# 搜索邮件
mail-cli mail search --fid INBOX --keyword "report" --limit 10
mail-cli mail search --fid INBOX --from "boss@example.com" --unread
mail-cli mail search --fid INBOX --keyword "invoice" --fts # 全文搜索

# 移动邮件到其他文件夹
mail-cli mail move --ids "msg1,msg2" --to-fid Trash --fid INBOX

# 标记邮件已读/未读
mail-cli mail mark --ids "msg1,msg2" --fid INBOX --read
mail-cli mail mark --ids "msg1" --fid INBOX --unread
mail list 选项：

选项	说明
--fid <id>	文件夹 ID 或路径（必填）
--order <field>	排序字段
--desc	降序排列
--limit <n>	限制返回数量
--start <n>	分页偏移量
--unread	仅显示未读邮件
mail search 选项：

选项	说明
--fid <folder>	文件夹 ID 或路径（必填）
--keyword <text>	在主题/发件人/收件人中搜索（配合 --fts 可搜索正文）
--from <addr>	按发件人过滤
--to <addr>	按收件人过滤
--subject <text>	按主题过滤
--since <date>	该日期之后的邮件（含当天）
--before <date>	该日期之前的邮件（不含当天）
--unread	仅搜索未读邮件
--fts	全文搜索（搜索邮件正文，需配合 --keyword 使用）
--limit <n>	限制返回数量（默认 50）
--keyword 默认搜索主题/发件人/收件人。加上 --fts 后切换为全文正文搜索（Ajax 使用 FTS 引擎；IMAP 使用 BODY 搜索）。在 Ajax FTS 模式下，--from/--to 等细粒度过滤器会被忽略并显示警告。

mail move 选项：

选项	说明
--ids <id1,id2>	邮件 ID，逗号分隔（必填）
--to-fid <folder>	目标文件夹（必填）
--fid <folder>	源文件夹（IMAP 账户必填）
mail mark 选项：

选项	说明
--ids <id1,id2>	邮件 ID，逗号分隔（必填）
--fid <folder>	文件夹（IMAP 账户必填）
--read	标记为已读
--unread	标记为未读
--read 和 --unread 互斥，必须指定其中一个。

read -- 阅读邮件内容
read body -- 查看邮件正文
读取并显示邮件正文。默认将 HTML 转换为纯文本在终端显示。

# 显示转换后的纯文本
mail-cli read body --id <message-id>

# 显示原始 HTML
mail-cli read body --id <message-id> --raw

# 保存 HTML 到文件
mail-cli read body --id <message-id> --out-file body.html

# 以 JSON 格式输出
mail-cli read body --id <message-id> --json

# IMAP 账户需要指定 --fid
mail-cli read body --id <message-id> --fid INBOX
read header -- 查看邮件头
显示邮件头信息（发件人、收件人、主题、日期等）。

mail-cli read header --id <message-id>
mail-cli read header --id <message-id> --fid INBOX
mail-cli read header --id <message-id> --json
read structure -- 查看 MIME 结构
查看邮件的 MIME 结构和附件列表。

mail-cli read structure --id <message-id>
mail-cli read structure --id <message-id> --fid INBOX
输出为 MIME 各部分的表格，包含内容类型、大小和文件名。

read attachment -- 下载附件
按 Part ID 下载指定附件。Part ID 可通过 read structure 查看。

# 下载到当前目录（使用原始文件名）
mail-cli read attachment --id <message-id> --part <part-id>

# 下载到指定文件
mail-cli read attachment --id <message-id> --part <part-id> --out-file report.pdf

# 下载到指定目录（使用原始文件名）
mail-cli read attachment --id <message-id> --part <part-id> --out-file ./downloads/

# IMAP 账户需要指定 --fid
mail-cli read attachment --id <message-id> --part <part-id> --fid INBOX
compose -- 写信与发送
# 基本发送
mail-cli compose send --to "a@example.com" --subject "Hello" --body "World"

# 带抄送和密送
mail-cli compose send --to "a@b.com" --cc "c@d.com" --bcc "e@f.com" --subject "Test" --body "Hi"

# 发送 HTML 正文
mail-cli compose send --to "a@b.com" --subject "HTML" --body "<h1>Hello</h1>" --html

# 从文件读取正文
mail-cli compose send --to "a@b.com" --subject "Report" --body-file ./email.html --html

# 添加附件（可重复使用）
mail-cli compose send --to "a@b.com" --subject "Files" --body "See attached" \
--attach report.pdf --attach data.csv

# 设置优先级（1-5，默认 3）
mail-cli compose send --to "a@b.com" --subject "Urgent" --body "!" --priority 1
mail watch — 实时邮件推送
通过 WebSocket 长连接监听新邮件，输出 NDJSON（每行一个 JSON）。

# 基础用法：实时打印新邮件完整详情（NDJSON，每行一封）
mail-cli mail watch

# 抑制 stderr 状态/调试日志（仅保留 stdout 数据流）
mail-cli mail watch --quiet

# 原始模式：输出所有 WS 包（recv/pong/disconnect/unknown），不拉取邮件详情
mail-cli mail watch --raw

# 指定账号 profile
mail-cli --profile work mail watch --quiet
stdout 输出格式（NDJSON）：

默认模式下，每封新邮件到达时输出一行 JSON（完整字段）：

{"id":"55:1tbiNwkGDGnYrSl8OgAA3H","from":["111 <qtest_xxx@163.com>"],"to":["user@claw.163.com"],"cc":[],"bcc":[],"subject":"test22","date":"2026-04-10 15:56:24","priority":3,"text":"hello","html":"<div ...>...</div>","attachments":[],"headerRaw":"Received: ..."}
字段	说明
id	邮件 ID，可传给 read body、read attachment 等命令
from	发件人地址数组
to / cc / bcc	收件人、抄送、密送地址数组
subject	邮件主题
date	邮件时间字符串（由服务端返回，格式不保证固定为 ISO 8601）
priority	优先级（通常 1-5）
text / html	邮件正文文本/HTML（可能为空）
attachments	附件列表
headerRaw	原始邮件头
--raw 模式示例（结构会随包类型变化）：

{"packetType":"recv","messageID":2042512010918137900,"messageSeq":1,"fromUID":"system","channelID":"system","channelType":1,"payload":"{\"type\":3001,\"mailId\":\"55:...\"}"}
选项：

选项	说明
--quiet	不输出 watch 状态与 WsClient 调试日志（仅保留 stdout 数据；致命/错误信息仍可能输出到 stderr）
--ws-url <url>	覆盖 WebSocket 服务器地址（默认 wss://claw.126.net:5210）
--raw	输出所有 WebSocket 包的 NDJSON（不筛选 type=3001，不调用读信接口）
断线重连策略： 1s → 2s → 4s → 8s → 16s，超过 5 次退出并返回非零状态码。

与 Claude 集成（mail watch + Claude）
mail watch 的 NDJSON 流设计专为 AI 管道化场景优化：状态日志在 stderr，干净的数据流在 stdout，可以直接管道给任何 LLM 工具。

默认模式下每条记录已经包含 subject/from/text/html 等常用字段，通常不需要再额外调用 read body。如需控制 token，可优先传 text，并截断或忽略 html/headerRaw。

方式一：Shell 管道（最简单）
使用 Claude CLI，将每封新邮件实时送给 Claude 处理：

mail-cli --profile work mail watch --quiet | while IFS= read -r line; do
# 直接使用 watch 输出中的字段，避免再次 read body
payload=$(echo "$line" | python3 -c 'import sys,json; d=json.load(sys.stdin); print(json.dumps({
"id": d.get("id",""),
"from": (d.get("from") or [""])[0],
"subject": d.get("subject",""),
"text": d.get("text",""),
"date": d.get("date","")
}, ensure_ascii=False))')

# 让 Claude 分析并决定是否需要回复
echo "$payload" | claude -p "你是一个邮件助手。输入是单封邮件的 JSON（含 id/from/subject/text/date）。分析这封邮件，如果需要回复请给出回复草稿（中文），否则输出'无需回复'。"
done
ClawEmail Documentation · claw.163.com
