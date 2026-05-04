# watch_account 异常 [WinError 2] 系统找不到指定的文件 — 根因分析

## 现象

启动 `scripts/dev.ps1` 后，watcher 每 5 秒尝试重启 mail-cli 监听，持续报错：

```
ERROR __main__ watch_account 异常 [mail1]: [WinError 2] 系统找不到指定的文件。
ERROR __main__ watch_account 异常 [mail2]: [WinError 2] 系统找不到指定的文件。
```

Web 服务（FastAPI）正常启动，访问 `http://127.0.0.1:8000` 返回 401（Basic Auth 正常）。

---

## 代码定位

异常发生在 [app/watcher.py](file:///d:/进阶指南/ClawMail-panel/app/watcher.py) 第 22–28 行：

```python
process = subprocess.Popen(
    ["mail-cli", "--profile", account.profile, "mail", "watch", "--quiet"],
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True,
    encoding="utf-8",
)
```

`subprocess.Popen` 抛出 `FileNotFoundError`（Windows 下显示为 `[WinError 2] 系统找不到指定的文件`）。

---

## 根因分析

### 1. `shutil.which("mail-cli")` 在 PowerShell 中能找到，但 `subprocess.Popen` 找不到

在 PowerShell 终端中验证：

```powershell
Get-Command mail-cli | Select-Object Source
# 输出: D:\DevTools\npm-global\mail-cli.ps1
```

`mail-cli` 实际上是一个 **PowerShell 脚本（`mail-cli.ps1`）**，由 npm 全局安装时生成。

### 2. `subprocess.Popen` 默认行为差异

- 在 Windows 上，`subprocess.Popen` 默认参数 `shell=False`
- 当 `shell=False` 时，Windows 使用 `CreateProcessW` API，它**只能执行 `.exe`、`.bat`、`.cmd` 等可执行文件**
- `CreateProcessW` **不会自动调用 PowerShell 来执行 `.ps1` 脚本**，因此找不到 `mail-cli.exe` 或 `mail-cli.bat`，直接报 `WinError 2`

### 3. 为什么 `shutil.which()` 能通过？

`shutil.which()` 查找的是 PATH 中的文件，它会找到 `mail-cli.ps1`，但 `subprocess.Popen(..., shell=False)` 无法直接执行 `.ps1` 文件。

### 4. 与 `mail-cli auth test` 失败的关联

虽然 `mail-cli --profile mail1 auth test` 返回 `JWT_FETCH_FAILED`（API Key 问题），但这说明在**当前 PowerShell 终端中 `mail-cli` 命令是可用的**。进一步证明问题出在 `subprocess.Popen` 的执行方式上，而不是 `mail-cli` 未安装。

---

## 结论

**根因**：`subprocess.Popen` 在 `shell=False` 模式下无法直接执行 PowerShell 脚本（`.ps1`），而 npm 全局安装的 `mail-cli` 入口正是 `mail-cli.ps1`，导致 `CreateProcessW` 报 `WinError 2`。

---

## 修复方案

### 方案一：使用 `shell=True`（推荐，改动最小）

将命令改为字符串形式，并设置 `shell=True`，让 Windows 通过 `cmd.exe` 执行，由 shell 解析 PATH 并调用 PowerShell 脚本：

```python
process = subprocess.Popen(
    f"mail-cli --profile {account.profile} mail watch --quiet",
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True,
    encoding="utf-8",
    shell=True,
)
```

**注意**：`shell=True` 有潜在安全风险，但在本地运行、命令参数可控（来自配置文件）的场景下可以接受。

### 方案二：显式调用 PowerShell 执行

```python
process = subprocess.Popen(
    ["powershell", "-Command", "mail-cli", "--profile", account.profile, "mail", "watch", "--quiet"],
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True,
    encoding="utf-8",
)
```

**缺点**：绑定 PowerShell，跨平台兼容性差。

### 方案三：查找 `mail-cli` 的真实可执行路径

使用 `shutil.which("mail-cli")` 获取完整路径，但需要注意：
- 如果返回的是 `.ps1` 路径，仍需用 PowerShell 执行
- 如果 npm 同时生成了 `.cmd` 文件（如 `mail-cli.cmd`），可以直接执行 `.cmd`

验证是否存在 `.cmd`：
```powershell
Get-Command mail-cli.cmd -ErrorAction SilentlyContinue
```

### 方案四：修改 `dev.ps1` 启动方式（绕过 watcher.py）

在 `dev.ps1` 中直接在前台启动 `mail-cli mail watch`，通过管道或其他方式处理输出。但这会改变架构，不推荐。

---

## 推荐修复

采用**方案一**（`shell=True`），在 [app/watcher.py](file:///d:/进阶指南/ClawMail-panel/app/watcher.py) 第 22–28 行修改：

```python
process = subprocess.Popen(
    f"mail-cli --profile {account.profile} mail watch --quiet",
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True,
    encoding="utf-8",
    shell=True,
)
```

同时建议增加对 `mail-cli` 是否可执行的预检查，或捕获 `FileNotFoundError` 给出更友好的错误提示：

```python
except FileNotFoundError as e:
    logger.error(
        "mail-cli 无法执行 [%s]: %s。请确保 mail-cli 已正确安装并在 PATH 中。",
        account.profile, e
    )
```

---

## 验证步骤

1. 修改 `app/watcher.py`，添加 `shell=True`
2. 重新运行 `scripts/dev.ps1`
3. 观察日志是否还有 `WinError 2`
4. 检查 `mail-cli` 是否正常输出 NDJSON 数据
