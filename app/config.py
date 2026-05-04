import json
import logging
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class Account:
    profile: str
    email: str
    display_name: str


@dataclass
class AppConfig:
    enabled: bool
    accounts: list[Account] = field(default_factory=list)
    db_path: str = ""
    basic_auth_user: str = ""
    basic_auth_password: str = ""


def load_config(path: str) -> AppConfig:
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        logger.error("配置文件不存在: %s", path)
        raise

    required_fields = ["enabled"]
    for key in required_fields:
        if key not in data:
            logger.error("配置字段缺失: %s", key)
            raise ValueError(f"配置字段缺失: {key}")

    accounts = []
    if "accounts" in data:
        for i, item in enumerate(data["accounts"]):
            account_required = ["profile", "email", "display_name"]
            for key in account_required:
                if key not in item:
                    logger.error("accounts[%d] 配置字段缺失: %s", i, key)
                    raise ValueError(f"accounts[{i}] 配置字段缺失: {key}")
            accounts.append(Account(
                profile=item["profile"],
                email=item["email"],
                display_name=item["display_name"],
            ))

    config = AppConfig(
        enabled=data["enabled"],
        accounts=accounts,
        db_path=data.get("db_path", ""),
        basic_auth_user=data.get("basic_auth_user", ""),
        basic_auth_password=data.get("basic_auth_password", ""),
    )
    logger.info("配置加载成功: %d 个账号, db_path=%s", len(accounts), config.db_path)
    return config
