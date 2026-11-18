import mimetypes
import os
from pathlib import Path

from flask import Flask, render_template, jsonify, send_file, request

from parser import parse_whatsapp_backup, _MEDIA_ATTACH_PATTERNS


def _clean_media_caption(text: str, media_file=None) -> str:
    """Drop leading WhatsApp attachment indicator line, keeping only real captions."""
    if not text:
        return ""
    lines = text.splitlines()
    first = lines[0].lstrip("\u200e\u200f\ufeff").strip()
    is_attach = any(p.match(first) for p in _MEDIA_ATTACH_PATTERNS) or (
        bool(media_file) and first == media_file
    )
    if is_attach:
        return "\n".join(lines[1:]).strip()
    return text.strip()


def _format_doc_size(num_bytes: int) -> str:
    """Format file size in bytes as B, KB, or MB for document cards."""
    if num_bytes < 1024:
        return f"{num_bytes} B"
    if num_bytes < 1024 * 1024:
        return f"{max(1, round(num_bytes / 1024))} KB"
    return f"{num_bytes / (1024 * 1024):.1f} MB"

mimetypes.add_type("audio/ogg", ".opus")

_BASE = Path(os.environ.get("APP_BASE", str(Path(__file__).parent)))
_BUNDLE = Path(os.environ.get("APP_BUNDLE", str(Path(__file__).parent)))

app = Flask(__name__, template_folder=str(_BUNDLE / "templates"),
           static_folder=str(_BUNDLE), static_url_path="/static")
app.config["MAX_CONTENT_LENGTH"] = 200 * 1024 * 1024

CHATS_DIR = _BASE / "chats"
_MEDIA_EXTS = {
    ".jpg", ".jpeg", ".png", ".heic", ".webp", ".gif",
    ".mp4", ".mov", ".avi", ".3gp", ".mkv",
    ".opus", ".ogg", ".mp3", ".m4a", ".aac",
    ".pdf", ".docx", ".xlsx", ".doc", ".xls", ".apk",
}
_msg_cache: dict = {}


# Solo la propia ventana de la app: el servidor escucha en 127.0.0.1, pero una
# página web abierta en el navegador podría apuntarle un dominio propio (DNS
# rebinding) y leer los chats, o enviarle peticiones (CSRF). Se exige Host local
# y, en lo que no es lectura, que venga del mismo origen.
_LOCAL_HOSTS = {"127.0.0.1", "localhost"}


@app.before_request
def _solo_peticiones_locales():
    host = (request.host or "").rsplit(":", 1)[0].strip("[]").lower()
    if host not in _LOCAL_HOSTS:
        return jsonify({"error": "Host no permitido"}), 403
    if request.method not in ("GET", "HEAD", "OPTIONS"):
        origin = request.headers.get("Origin")
        if origin is not None and origin.rstrip("/") != request.host_url.rstrip("/"):
            return jsonify({"error": "Origen no permitido"}), 403
        site = request.headers.get("Sec-Fetch-Site")
        if site is not None and site not in ("same-origin", "none"):
            return jsonify({"error": "Origen no permitido"}), 403
    return None


@app.after_request
def no_cache(response):
    response.headers["Cache-Control"] = "no-store"
    return response


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/chats")
def list_chats():
    _msg_cache.clear()
    CHATS_DIR.mkdir(parents=True, exist_ok=True)
    chats = []
    for folder in sorted(CHATS_DIR.iterdir()):
        if not folder.is_dir():
            continue
        txt_files = list(folder.glob("*.txt"))
        if not txt_files:
            continue
        media_count = sum(
            1 for f in folder.iterdir()
            if f.is_file() and f.suffix.lower() in _MEDIA_EXTS
        )
        chats.append({"name": folder.name, "mediaCount": media_count})
    return jsonify(chats)


@app.route("/api/chats/<name>/messages")
def get_chat_messages(name):
    if name in _msg_cache:
        return jsonify(_msg_cache[name])
    try:
        folder = CHATS_DIR / name
        if not folder.is_dir():
            return jsonify({"error": "Chat no encontrado"}), 404

        txt_files = list(folder.glob("*.txt"))
        if not txt_files:
            return jsonify({"error": "No se encontro archivo .txt"}), 404

        content = txt_files[0].read_text(encoding="utf-8", errors="replace")
        parsed = parse_whatsapp_backup(content)
        if not parsed:
            return jsonify({"error": "No se encontraron mensajes"}), 400

        file_sizes = {f.name: f.stat().st_size for f in folder.iterdir() if f.is_file()}
        existing = set(file_sizes)
        senders = sorted({m.sender for m in parsed if m.sender != "Sistema"})
        my_name = "Tú" if "Tú" in senders else ("You" if "You" in senders else (senders[0] if senders else ""))

        messages = []
        for m in parsed:
            text = _clean_media_caption(m.text, m.media_file) if m.media_type else m.text
            msg = {
                "date": m.date, "time": m.time, "sender": m.sender,
                "text": text,
            }
            if m.media_type:
                msg["mt"] = m.media_type
                if m.media_file:
                    msg["mf"] = m.media_file
                    msg["me"] = m.media_file in existing
                    if m.media_type == "document" and m.media_file in file_sizes:
                        ext = Path(m.media_file).suffix.lstrip(".").upper() or "FILE"
                        msg["meta"] = f"{ext} · {_format_doc_size(file_sizes[m.media_file])}"
            messages.append(msg)

        result = {
            "name": name,
            "senders": senders,
            "myName": my_name,
            "messages": messages,
        }
        _msg_cache[name] = result
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/chats/<name>/media/<path:filename>")
def serve_media(name, filename):
    folder = CHATS_DIR / name
    file_path = folder / filename
    try:
        if not file_path.resolve().is_relative_to(folder.resolve()):
            return jsonify({"error": "Acceso no permitido"}), 403
    except ValueError:
        return jsonify({"error": "Ruta invalida"}), 400
    if not file_path.is_file():
        return jsonify({"error": "Archivo no encontrado"}), 404
    return send_file(file_path)


