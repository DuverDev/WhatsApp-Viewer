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
