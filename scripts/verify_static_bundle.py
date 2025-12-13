"""
Builds the frontend, syncs the dist output into backend/static, and verifies
the FastAPI app can serve the generated index without Node.js running.
"""

from importlib import import_module, reload
import os
from pathlib import Path
import shutil
import subprocess
import sys

from fastapi.testclient import TestClient


ROOT = Path(__file__).resolve().parent.parent
FRONTEND_DIR = ROOT / "frontend"
BACKEND_DIR = ROOT / "backend"
DIST_DIR = FRONTEND_DIR / "dist"
STATIC_DIR = BACKEND_DIR / "static"


def run(cmd, cwd: Path) -> None:
    print(f"$ {' '.join(cmd)}")
    subprocess.run(cmd, cwd=cwd, check=True)


def ensure_frontend_deps() -> None:
    if (FRONTEND_DIR / "node_modules").exists():
        return
    run(["npm", "install"], FRONTEND_DIR)


def build_frontend() -> None:
    run(["npm", "run", "build"], FRONTEND_DIR)
    if not DIST_DIR.exists():
        raise RuntimeError("frontend build did not produce a dist directory")


def sync_static() -> None:
    STATIC_DIR.mkdir(parents=True, exist_ok=True)
    shutil.copytree(DIST_DIR, STATIC_DIR, dirs_exist_ok=True)


def verify_static_route() -> None:
    os.environ["STATIC_DIR"] = str(STATIC_DIR)
    sys.path.insert(0, str(BACKEND_DIR))
    app_module = import_module("app.main")
    app_module = reload(app_module)
    client = TestClient(app_module.app)
    response = client.get("/static/index.html")
    if response.status_code != 200:
        raise RuntimeError(f"/static/index.html returned {response.status_code}")
    print("Static bundle served successfully via FastAPI")


def main() -> None:
    ensure_frontend_deps()
    build_frontend()
    sync_static()
    verify_static_route()
    print("Frontend built, assets copied, backend serving without Node.js runtime.")


if __name__ == "__main__":
    main()
