from __future__ import annotations

import json
from dataclasses import dataclass


@dataclass
class Email:
    id: int
    profile: str
    account_name: str | None
    mail_id: str
    sender: str | None
    recipients: str | None
    cc: str | None
    subject: str | None
    date_text: str | None
    text_body: str | None
    html_body: str | None
    attachments_json: str | None
    header_raw: str | None
    raw_json: str | None
    is_read: int = 0
    created_at: str | None = None

    @classmethod
    def from_dict(cls, data: dict) -> Email:
        return cls(
            id=data["id"],
            profile=data["profile"],
            account_name=data.get("account_name"),
            mail_id=data["mail_id"],
            sender=data.get("sender"),
            recipients=data.get("recipients"),
            cc=data.get("cc"),
            subject=data.get("subject"),
            date_text=data.get("date_text"),
            text_body=data.get("text_body"),
            html_body=data.get("html_body"),
            attachments_json=data.get("attachments_json"),
            header_raw=data.get("header_raw"),
            raw_json=data.get("raw_json"),
            is_read=data.get("is_read", 0),
            created_at=data.get("created_at"),
        )

    @property
    def attachments(self) -> list:
        if not self.attachments_json:
            return []
        try:
            result = json.loads(self.attachments_json)
            return result if isinstance(result, list) else []
        except (json.JSONDecodeError, TypeError):
            return []
