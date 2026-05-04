# 计划：支持 per-profile API Key，实现多主邮箱同时在线

## 问题

mail-cli 只支持**全局单一 API Key**（通过 `apikeyRef` 引用系统钥匙串中的条目）。当配置两个独立主邮箱时，只有一个 API Key 生效，另一个账号因 API Key 不匹配而认证失败：

```
mail1 ✗ failed to obtain access token, please check your API key
mail2 ✓ ok
```

## 根因

mail-cli 配置文件 (`C:\Users\huang\AppData\Roaming\mail-cli\config.json`) 结构：

```json
{
  "profiles": {
    "mail1": { "user": "kapathy@claw.163.com" },
    "mail2": { "user": "moonshot@claw.163.com" }
  },
  "apikeyRef": "mail-cli:apikey",
  "default": "mail1"
}
```

`apikeyRef` 是全局配置，不在 profile 内部。所有 profile 共用同一个钥匙串条目。

## 方案演进

### 方案 A（已放弃）：`--config` 独立配置文件

为每个账号生成独立的 mail-cli 配置文件，每个配置文件拥有自己的 `apikeyRef`。

**放弃原因**：实测发现 `--config` 指定独立配置文件后，`auth apikey set` 虽然报告成功，但 `auth login` 和 `auth test` 仍然报 JWT_FETCH_FAILED。推测 mail-cli 的钥匙串集成在 `--config` 模式下存在 bug 或限制，无法正确读取 per-config 的 apikeyRef。

### 方案 B（已采用）：启动前切换全局 API Key

在启动每个 `mail watch` 进程前，先切换全局 API Key 为该账号的 key，然后启动进程。mail-cli 进程启动后会缓存 API Key，后续 JWT 刷新使用内存中的缓存。

**关键机制**：
1. JWT token 缓存在 `C:\Users\huang\AppData\Roaming\mail-cli\tokens\<email>.json`
2. `mail watch` 启动时用 API Key 获取 JWT，之后 JWT 缓存在内存中
3. 使用线程锁 (`_apikey_lock`) 保证"设置 API Key → 启动进程 → 等待初始化"的原子性
4. 进程重启时重新设置正确的 API Key

## 最终实现

### 修改文件

| 文件 | 修改内容 |
|------|----------|
| `app/config.py` | Account 增加 `api_key` 字段，load_config 读取 |
| `app/watcher.py` | 新增 `_set_apikey_and_login()`、`_run_mail_cli()`，修改 `watch_account()` 和 `start_watchers()` |
| `config.example.json` | 增加 `api_key` 字段示例 |

### 启动流程

```
start_watchers()
  ├── 阶段1：逐个初始化账号（串行，带锁）
  │   ├── _set_apikey_and_login(mail1)
  │   │   ├── mail-cli auth apikey set <mail1_key>   ← 切换全局 API Key
  │   │   └── mail-cli --profile mail1 auth login    ← 获取并缓存 JWT
  │   └── _set_apikey_and_login(mail2)
  │       ├── mail-cli auth apikey set <mail2_key>   ← 切换全局 API Key
  │       └── mail-cli --profile mail2 auth login    ← 获取并缓存 JWT
  │
  ├── 阶段2：逐个启动监听线程（间隔3秒，带锁）
  │   ├── watch_account(mail1)
  │   │   ├── [锁内] mail-cli auth apikey set <mail1_key>
  │   │   ├── [锁内] Popen("mail-cli --profile mail1 mail watch --quiet")
  │   │   └── [锁内] sleep(2) 等待进程初始化
  │   └── watch_account(mail2)
  │       ├── [锁内] mail-cli auth apikey set <mail2_key>
  │       ├── [锁内] Popen("mail-cli --profile mail2 mail watch --quiet")
  │       └── [锁内] sleep(2) 等待进程初始化
  │
  └── 完成：两个账号同时在线监听
```

### 断线重连流程

```
mail watch 进程退出（JWT 过期 / 连接断开）
  ↓
watch_account 循环重试
  ├── [锁内] mail-cli auth apikey set <该账号的key>   ← 重新设置正确的 key
  ├── [锁内] Popen("mail-cli --profile <p> mail watch --quiet")
  └── [锁内] sleep(2)
```

## 验证结果

- ✅ 两个 mail-cli-binary 进程同时运行
- ✅ 无 "failed to obtain IM token" 错误
- ✅ Web 服务正常启动
- ✅ 向后兼容：未配置 api_key 的账号使用默认 mail-cli 配置

## 注意事项

1. **JWT 刷新**：当 JWT 过期需要刷新时，mail-cli 进程可能因 API Key 不匹配而退出。watcher 会在重启时重新设置正确的 API Key。这意味着每 ~30 分钟可能有短暂断连。
2. **线程安全**：`_apikey_lock` 保证 API Key 设置和进程启动的原子性，避免多线程竞争。
3. **向后兼容**：`api_key` 字段为可选，未配置时使用原始的 `--profile` 方式启动。
