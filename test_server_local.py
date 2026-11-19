"""El servidor local solo atiende a la propia ventana de la app (DNS rebinding y CSRF)."""
from server import app


def _client():
    app.config["TESTING"] = True
    return app.test_client()


def test_host_ajeno_bloqueado():
    assert _client().get("/api/chats", base_url="http://atacante.example:5000").status_code == 403


def test_media_con_host_ajeno_bloqueado():
    r = _client().get("/api/chats/demo/media/foto.jpg", base_url="http://atacante.example:5000")
    assert r.status_code == 403


def test_host_local_permitido():
    assert _client().get("/api/chats", base_url="http://127.0.0.1:5000").status_code == 200


def test_localhost_permitido():
    assert _client().get("/", base_url="http://localhost:5000").status_code == 200


def test_post_desde_otro_sitio_bloqueado():
    r = _client().post("/api/chats", base_url="http://127.0.0.1:5000",
                       headers={"Origin": "https://atacante.example", "Sec-Fetch-Site": "cross-site"})
    assert r.status_code == 403


def _chat_con_adjuntos(tmp, monkeypatch):
    import server
    from pathlib import Path
    carpeta = Path(tmp) / "Amigo"
    carpeta.mkdir()
    (carpeta / "chat.txt").write_text("1/11/26, 10:00 - Amigo: hola\n", encoding="utf-8")
    script = '<script>fetch("/api/chats")</script>'
    (carpeta / "factura.html").write_text(script, encoding="utf-8")
    (carpeta / "dibujo.svg").write_text(f'<svg xmlns="http://www.w3.org/2000/svg">{script}</svg>', encoding="utf-8")
    (carpeta / "foto.jpg").write_bytes(b"\xff\xd8\xff\xe0")
    (carpeta / "doc.pdf").write_bytes(b"%PDF-1.4")
    monkeypatch.setattr(server, "CHATS_DIR", Path(tmp))


def test_adjunto_html_o_svg_no_se_ejecuta(tmp_path, monkeypatch):
    """SEC-086: un .html o .svg recibido por WhatsApp no corre en el origen de la app."""
    _chat_con_adjuntos(tmp_path, monkeypatch)
    for nombre in ("factura.html", "dibujo.svg"):
        r = _client().get(f"/api/chats/Amigo/media/{nombre}", base_url="http://127.0.0.1:5000")
        assert r.status_code == 200
        assert r.headers["Content-Type"] == "application/octet-stream"
        assert r.headers["Content-Disposition"].startswith("attachment")
        assert r.headers["Content-Security-Policy"].startswith("sandbox")
        assert r.headers["X-Content-Type-Options"] == "nosniff"


def test_imagen_y_pdf_se_muestran(tmp_path, monkeypatch):
    _chat_con_adjuntos(tmp_path, monkeypatch)
    foto = _client().get("/api/chats/Amigo/media/foto.jpg", base_url="http://127.0.0.1:5000")
    assert foto.headers["Content-Type"] == "image/jpeg"
    assert foto.headers["Content-Disposition"].startswith("inline")
    pdf = _client().get("/api/chats/Amigo/media/doc.pdf", base_url="http://127.0.0.1:5000")
    assert pdf.headers["Content-Type"] == "application/pdf"
    assert pdf.headers["Content-Disposition"].startswith("inline")
    assert "Content-Security-Policy" not in pdf.headers
