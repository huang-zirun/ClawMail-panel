import json
import logging
import shutil
import subprocess
import threading
import time

from app.config import Account, AppConfig, load_config
from app.database import init_db, insert_email

logger = logging.getLogger(__name__)

_apikey_lock = threading.Lock()


def _run_mail_cli(args: str, timeout: int = 30) -> tuple[int, str, str]:
    cmd = f"mail-cli {args}"
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            shell=True,
            timeout=timeout,
        )
        return result.returncode, result.stdout.strip(), result.stderr.strip()
    except subprocess.TimeoutExpired:
        return -1, "", "timeout"
    except Exception as e:
        return -1, "", str(e)


def _set_apikey_and_login(account: Account) -> bool:
    if not account.api_key:
        logger.error("账号 %s 缺少 api_key，跳过", account.profile)
        return False

    with _apikey_lock:
        rc, _, err = _run_mail_cli(f"auth apikey set {account.api_key}")
        if rc != 0:
            logger.error("写入 API Key 失败 [%s]: %s", account.profile, err)
            return False
        logger.info("API Key 已设置 [%s]", account.profile)

        rc, _, err = _run_mail_cli(f"--profile {account.profile} auth login --user {account.email}")
        if rc != 0:
            logger.error("登录失败 [%s]: %s", account.profile, err)
            return False
        logger.info("登录成功 [%s]", account.profile)

    return True


def watch_account(account: Account, db_path: str):
    if shutil.which("mail-cli") is None:
        logger.error("mail-cli 未安装，无法启动监听: profile=%s", account.profile)
        return

    while True:
        logger.info("启动邮件监听: profile=%s, account=%s", account.profile, account.display_name)
        try:
            if account.api_key:
                with _apikey_lock:
                    rc, _, err = _run_mail_cli(f"auth apikey set {account.api_key}")
                    if rc != 0:
                        logger.error("设置 API Key 失败 [%s]: %s", account.profile, err)
                        time.sleep(5)
                        continue

                    process = subprocess.Popen(
                        f"mail-cli --profile {account.profile} mail watch --quiet",
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True,
                        encoding="utf-8",
                        shell=True,
                    )

                    time.sleep(2)

            else:
                process = subprocess.Popen(
                    f"mail-cli --profile {account.profile} mail watch --quiet",
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    encoding="utf-8",
                    shell=True,
                )

            def _read_stderr():
                for line in process.stderr:
                    line = line.rstrip("\n")
                    if line:
                        logger.warning("mail-cli stderr [%s]: %s", account.profile, line)

            stderr_thread = threading.Thread(target=_read_stderr, daemon=True)
            stderr_thread.start()

            for line in process.stdout:
                line = line.rstrip("\n")
                if not line:
                    continue
                try:
                    data = json.loads(line)
                except json.JSONDecodeError:
                    logger.error("JSON 解析失败 [%s]: %s", account.profile, line)
                    continue

                email_data = {
                    "mail_id": data.get("id", ""),
                    "sender": ",".join(data.get("from", [])),
                    "recipients": ",".join(data.get("to", [])),
                    "cc": ",".join(data.get("cc", [])),
                    "subject": data.get("subject", ""),
                    "date_text": data.get("date", ""),
                    "text_body": data.get("text", ""),
                    "html_body": data.get("html", ""),
                    "attachments_json": json.dumps(data.get("attachments", []), ensure_ascii=False),
                    "header_raw": data.get("headerRaw", ""),
                    "raw_json": line,
                    "profile": account.profile,
                    "account_name": account.display_name,
                }
                insert_email(db_path, email_data)

            process.wait()
            logger.warning("mail-cli 进程退出 [%s]，5 秒后重启", account.profile)
        except Exception as e:
            logger.error("watch_account 异常 [%s]: %s", account.profile, e)

        time.sleep(5)


def start_watchers(config: AppConfig):
    init_db(config.db_path)

    ready_accounts = []
    for account in config.accounts:
        if account.api_key:
            if _set_apikey_and_login(account):
                ready_accounts.append(account)
            else:
                logger.error("账号 %s 初始化失败，跳过监听", account.profile)
        else:
            logger.warning("账号 %s 未配置 api_key，使用默认 mail-cli 配置", account.profile)
            ready_accounts.append(account)

    time.sleep(1)

    names = []
    for account in ready_accounts:
        t = threading.Thread(
            target=watch_account,
            args=(account, config.db_path),
            daemon=True,
        )
        t.start()
        names.append(f"{account.display_name}({account.profile})")
        time.sleep(3)

    logger.info("已启动邮件监听账号: %s", ", ".join(names))


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
    config = load_config("config.json")
    start_watchers(config)
    while True:
        time.sleep(1)
