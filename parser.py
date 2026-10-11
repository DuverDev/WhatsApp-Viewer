import re
from dataclasses import dataclass
from datetime import datetime, time
from typing import List, Optional

MESSAGE_PATTERN = re.compile(
    r"^(?P<date>\d{1,2}/\d{1,2}/\d{4}),\s*(?P<time>\d{1,2}:\d{2})\s*(?:a\.\s*m\.|p\.\s*m\.?)?\s*-\s*(?:(?P<sender>.*?)(?:\s*:\s*|\s+-\s*)(?P<message>.*)|(?P<system_message>.*))$",
    re.IGNORECASE,
)

_MEDIA_ATTACH = re.compile(
    r"^[‎‏‪‬⁦⁩]*(.+?)\s*\(archivo adjunto\)$"
)
_MEDIA_OMITTED = re.compile(
    r"^<[Mm]ultimedia omitido>$|^<[Mm]edia omitted>$"
)

_PREFIX_TYPE = {
    "IMG": "image", "PHOTO": "image",
    "VID": "video", "GIF": "video",
    "PTT": "audio", "AUD": "audio",
    "STK": "sticker",
}
_EXT_TYPE = {
    "jpg": "image", "jpeg": "image", "png": "image", "heic": "image",
    "mp4": "video", "mov": "video", "avi": "video", "3gp": "video", "mkv": "video",
    "opus": "audio", "ogg": "audio", "mp3": "audio", "m4a": "audio", "aac": "audio",
    "webp": "sticker",
    "pdf": "document", "docx": "document", "xlsx": "document", "pptx": "document",
    "doc": "document", "xls": "document", "txt": "document",
    "zip": "document", "rar": "document", "apk": "document",
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

    m = _MEDIA_ATTACH.match(stripped)
    if not m:
        return None, None

    filename = m.group(1).strip().lstrip("‎‏‪‬⁦⁩")
    prefix = filename.split("-")[0].upper() if "-" in filename else ""
    media_type = _PREFIX_TYPE.get(prefix)

    if not media_type:
        ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
        media_type = _EXT_TYPE.get(ext, "document")

    return media_type, filename


def parse_datetime(date_value: str, time_value: str) -> Optional[datetime]:
    for fmt in ("%d/%m/%Y %H:%M", "%m/%d/%Y %H:%M"):
        try:
            return datetime.strptime(f"{date_value} {time_value}", fmt)
        except ValueError:
            continue
    return None


def normalize_whatsapp_text(value: str) -> str:
    return (
        value.replace(" ", " ")
        .replace(" ", " ")
        .replace(" ", " ")
        .replace("​", "")
        .strip()
    )


def parse_whatsapp_backup(content: str) -> List[ChatMessage]:
    messages: List[ChatMessage] = []

    for raw_line in content.splitlines():
        line = normalize_whatsapp_text(raw_line)
        if not line:
            continue

        match = MESSAGE_PATTERN.match(line)
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

    for fmt in ("%d/%m/%Y", "%m/%d/%Y"):
        try:
            parsed = datetime.strptime(value.strip(), fmt)
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

    if sender and sender != "Todos":
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
