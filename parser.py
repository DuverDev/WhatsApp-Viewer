import re
from dataclasses import dataclass
from datetime import datetime, time
from typing import List, Optional

# Invisible Unicode characters frequently present in WhatsApp exports (e.g. iOS LTR/RTL marks, BOM)
_INVISIBLE_CHARS = "\u200e\u200f\u202a\u202b\u202c\u202d\u202e\u2066\u2067\u2068\u2069\ufeff\u200b"
_TRANSLATION_TABLE = str.maketrans({
    "\xa0": " ",
    "\u202f": " ",
    "\u2007": " ",
    **{c: "" for c in _INVISIBLE_CHARS}
})

# Android / Standard Web export pattern:
# e.g.: 12/10/2024, 20:15 - Ana: Hola
#       10/14/24, 9:30 PM - John: Hello
#       28/8/2021, 8:18 a. m. - Sistema: Cifrado...
MESSAGE_PATTERN_STANDARD = re.compile(
    r"^(?P<date>\d{1,4}[/\.-]\d{1,2}[/\.-]\d{2,4})[,\s]+(?P<time>\d{1,2}:\d{2}(?::\d{2})?(?:\s*(?:[ap]\.?\s*m\.?|[ap]m))?)\s*-\s*(?:(?P<sender>.*?)(?:\s*:\s*|\s+-\s*)(?P<message>.*)|(?P<system_message>.*))$",
    re.IGNORECASE,
)

# iOS Bracketed export pattern:
# e.g.: [12/10/2024, 20:15:30] Ana: Hola
#       [10/14/24, 9:30:15 PM] John: Hello
#       [12/31/23, 11:59:02 PM] Messages and calls are end-to-end encrypted.
MESSAGE_PATTERN_IOS = re.compile(
    r"^\[(?P<date>\d{1,4}[/\.-]\d{1,2}[/\.-]\d{2,4})[,\s]+(?P<time>\d{1,2}:\d{2}(?::\d{2})?(?:\s*(?:[ap]\.?\s*m\.?|[ap]m))?)\](?:\s*-\s*|\s+)(?:(?P<sender>[^:\n]+?):\s*(?P<message>.*)|(?P<system_message>.*))$",
    re.IGNORECASE,
)

MESSAGE_PATTERNS = [MESSAGE_PATTERN_STANDARD, MESSAGE_PATTERN_IOS]
MESSAGE_PATTERN = MESSAGE_PATTERN_STANDARD  # Backwards compatibility

_MEDIA_ATTACH_PATTERNS = [
    re.compile(r"^(.+?)\s*\((?:archivo adjunto|file attached)\)$", re.IGNORECASE),
    re.compile(r"^<(?:\s*attached|\s*adjunto)\s*:\s*(.+?)>$", re.IGNORECASE),
]
_MEDIA_OMITTED = re.compile(
    r"^<.*(?:omitido|omitted).*>$", re.IGNORECASE
)

_PREFIX_TYPE = {
    "IMG": "image", "PHOTO": "image",
    "VID": "video", "VIDEO": "video", "GIF": "video",
    "PTT": "audio", "AUD": "audio", "AUDIO": "audio",
    "STK": "sticker", "STICKER": "sticker",
    "DOC": "document",
}
_EXT_TYPE = {
    "jpg": "image", "jpeg": "image", "png": "image", "heic": "image",
    "mp4": "video", "mov": "video", "avi": "video", "3gp": "video", "mkv": "video",
    "opus": "audio", "ogg": "audio", "mp3": "audio", "m4a": "audio", "aac": "audio", "wav": "audio",
    "webp": "sticker",
    "pdf": "document", "docx": "document", "xlsx": "document", "pptx": "document",
    "doc": "document", "xls": "document", "txt": "document",
    "zip": "document", "rar": "document", "apk": "document", "csv": "document",
}


@dataclass
class ChatMessage:
    date: str
    time: str
    sender: str
    text: str
    raw: str
    media_type: Optional[str] = None
    media_file: Optional[str] = None

    @property
    def timestamp(self) -> str:
        return f"{self.date} {self.time}"

    @property
    def datetime_obj(self) -> Optional[datetime]:
        return parse_datetime(self.date, self.time)


def _detect_media(text: str):
    stripped = text.strip()

    if _MEDIA_OMITTED.match(stripped):
        return "omitted", None

    filename = None
    for pattern in _MEDIA_ATTACH_PATTERNS:
        m = pattern.match(stripped)
        if m:
            filename = m.group(1).strip()
            break

    if not filename:
        return None, None

    prefix = filename.split("-")[0].upper() if "-" in filename else ""
    media_type = _PREFIX_TYPE.get(prefix)

    if not media_type:
        ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
        media_type = _EXT_TYPE.get(ext, "document")

    return media_type, filename


def parse_datetime(date_value: str, time_value: str) -> Optional[datetime]:
    clean_time = (
        time_value.replace("a. m.", "AM")
        .replace("p. m.", "PM")
        .replace("a.m.", "AM")
        .replace("p.m.", "PM")
        .replace("am", "AM")
        .replace("pm", "PM")
        .strip()
    )
    clean_date = date_value.replace(".", "/").replace("-", "/").strip()
    date_time_str = f"{clean_date} {clean_time}"

    formats = (
        # 12h formats
        "%d/%m/%Y %I:%M %p",
        "%m/%d/%Y %I:%M %p",
        "%Y/%m/%d %I:%M %p",
        "%d/%m/%y %I:%M %p",
        "%m/%d/%y %I:%M %p",
        "%d/%m/%Y %I:%M:%S %p",
        "%m/%d/%Y %I:%M:%S %p",
        "%Y/%m/%d %I:%M:%S %p",
        "%d/%m/%y %I:%M:%S %p",
        "%m/%d/%y %I:%M:%S %p",
        # 24h formats
        "%d/%m/%Y %H:%M",
        "%m/%d/%Y %H:%M",
        "%Y/%m/%d %H:%M",
        "%d/%m/%y %H:%M",
        "%m/%d/%y %H:%M",
        "%d/%m/%Y %H:%M:%S",
        "%m/%d/%Y %H:%M:%S",
        "%Y/%m/%d %H:%M:%S",
        "%d/%m/%y %H:%M:%S",
        "%m/%d/%y %H:%M:%S",
    )
    for fmt in formats:
        try:
            return datetime.strptime(date_time_str, fmt)
        except ValueError:
            continue
    return None


def normalize_whatsapp_text(value: str) -> str:
    return value.translate(_TRANSLATION_TABLE).strip()


def parse_whatsapp_backup(content: str) -> List[ChatMessage]:
    messages: List[ChatMessage] = []

    for raw_line in content.splitlines():
        line = normalize_whatsapp_text(raw_line)
        if not line:
            continue

        match = None
        for pattern in MESSAGE_PATTERNS:
            match = pattern.match(line)
            if match:
                break

        if not match:
            if messages:
                prev = messages[-1]
                messages[-1] = ChatMessage(
                    date=prev.date, time=prev.time, sender=prev.sender,
                    text=prev.text + "\n" + line,
                    raw=prev.raw + "\n" + raw_line,
                    media_type=prev.media_type,
                    media_file=prev.media_file,
                )
            continue

        sender = (match.group("sender") or "Sistema").strip()
        message_text = (match.group("message") or match.group("system_message") or "").strip()

        if not sender and not message_text:
            continue

        if not match.group("message") and match.group("system_message"):
            sender = "Sistema"
            message_text = match.group("system_message").strip()

        media_type, media_file = _detect_media(message_text)

        messages.append(
            ChatMessage(
                date=match.group("date").strip(),
                time=match.group("time").strip(),
                sender=sender,
                text=message_text,
                raw=line,
                media_type=media_type,
                media_file=media_file,
            )
        )

    return messages


def _normalize_date(value: str, is_end: bool = False) -> Optional[datetime]:
    if not value:
        return None

    clean_date = value.replace(".", "/").replace("-", "/").strip()
    for fmt in ("%d/%m/%Y", "%m/%d/%Y", "%Y/%m/%d", "%d/%m/%y", "%m/%d/%y"):
        try:
            parsed = datetime.strptime(clean_date, fmt)
            return datetime.combine(parsed.date(), time(23, 59, 59) if is_end else time(0, 0))
        except ValueError:
            continue
    return None


def filter_messages(
    messages: List[ChatMessage],
    sender: Optional[str] = None,
    search: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
) -> List[ChatMessage]:
    result = list(messages)

    if sender and sender not in ("Todos", "All"):
        result = [msg for msg in result if msg.sender == sender]

    query = (search or "").strip().lower()
    if query:
        result = [
            msg
            for msg in result
            if query in msg.text.lower() or query in msg.sender.lower() or query in msg.raw.lower()
        ]

    start_dt = _normalize_date(start_date) if start_date else None
    end_dt = _normalize_date(end_date, is_end=True) if end_date else None

    if start_dt is not None:
        result = [
            msg for msg in result if (msg.datetime_obj is not None and msg.datetime_obj >= start_dt)
        ]

    if end_dt is not None:
        result = [
            msg for msg in result if (msg.datetime_obj is not None and msg.datetime_obj <= end_dt)
        ]

    return result


def group_messages_by_sender(messages: List[ChatMessage]):
    grouped = {}
    for message in messages:
        grouped.setdefault(message.sender, []).append(message)
    return dict(sorted(grouped.items()))
