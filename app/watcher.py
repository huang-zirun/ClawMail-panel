import json
import logging
import shutil
import subprocess
import threading
import time

from app.config import Account, AppConfig, load_config
from app.database import init_db, insert_email

logger = logging.getLogger(__name__)


def watch_account(account: Account, db_path: str):
    if shutil.which("mail-cli") is None:
        logger.error("mail-cli 未安装，无法启动监听: profile=%s", account.profile)
        return

    while True:
        logger.info("启动邮件监听: profile=%s, account=%s", account.profile, account.display_name)
        try:
            process = subprocess.Popen(
                ["mail-cli", "--profile", account.profile, "mail", "watch", "--quiet"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding="utf-8",
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
    names = []
    for account in config.accounts:
        t = threading.Thread(target=watch_account, args=(account, config.db_path), daemon=True)
        t.start()
        names.append(f"{account.display_name}({account.profile})")
    logger.info("已启动邮件监听账号: %s", ", ".join(names))


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
    config = load_config("config.json")
    start_watchers(config)
    while True:
        time.sleep(1)
