import re


CAPTCHA_PATTERNS = [
    re.compile(r"验证码[\s:：]*([A-Za-z0-9]{4,8})", re.IGNORECASE),
    re.compile(r"verification\s*code[\s:：]*([A-Za-z0-9]{4,8})", re.IGNORECASE),
    re.compile(r"code[\s:：]*([A-Za-z0-9]{4,8})", re.IGNORECASE),
    re.compile(r"\b(\d{4,8})\b"),
]


def extract_captcha(text: str | None) -> str | None:
    if not text:
        return None
    for pattern in CAPTCHA_PATTERNS:
        match = pattern.search(text)
        if match:
            candidate = match.group(1)
            if candidate and len(candidate) >= 4:
                return candidate
    return None
