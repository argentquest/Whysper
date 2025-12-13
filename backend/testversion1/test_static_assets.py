from importlib import reload

from fastapi.testclient import TestClient
import app.main as app_main


def test_static_dir_can_be_overridden(monkeypatch, tmp_path):
    static_dir = tmp_path / "static"
    static_dir.mkdir()
    index_file = static_dir / "index.html"
    index_file.write_text("static-ok")

    monkeypatch.setenv("STATIC_DIR", str(static_dir))
    reloaded = reload(app_main)

    client = TestClient(reloaded.app)
    response = client.get("/static/index.html")

    assert response.status_code == 200
    assert "static-ok" in response.text

    monkeypatch.delenv("STATIC_DIR", raising=False)
    reload(app_main)
