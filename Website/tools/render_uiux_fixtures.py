"""Render throwaway QA fixtures with Flask's test client, not a live server.

Usage: TECHVERSE_INSTANCE_DIR=<temporary-dir> python tools/render_uiux_fixtures.py <output-dir>
These files contain a synthetic QA account and must not be included in releases.
"""
from pathlib import Path
import json
import sys
import tempfile
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app import create_app, ROOT
from werkzeug.security import generate_password_hash

output = Path(sys.argv[1]).resolve()
output.mkdir(parents=True, exist_ok=True)
with tempfile.TemporaryDirectory(prefix="techverse-dom-") as directory:
    app = create_app({"TESTING": True, "DATABASE": str(Path(directory) / "qa.db"), "SECRET_KEY": "test-only",
                      "OPENAI_API_KEY": "", "STRIPE_SECRET_KEY": ""})
    client = app.test_client()
    for language in ("en", "ar"):
        with client.session_transaction() as session:
            session["language"] = language
        for name, route in (("public", "/"), ("login", "/login"), ("register", "/register"), ("contact", "/contact")):
            response = client.get(route)
            assert response.status_code == 200
            (output / f"{name}-{language}.html").write_text(response.get_data(as_text=True), encoding="utf-8")
    with app.app_context():
        db = app.get_db()
        uid = db.execute("INSERT INTO users(full_name,email,password,phone) VALUES(?,?,?,?)",
                         ("QA Account", "qa@example.invalid", generate_password_hash("test-password"), "+96170000000")).lastrowid
        db.commit()
    with client.session_transaction() as session:
        session["user_id"] = uid
        session["language"] = "en"
    for name, route in (("shop", "/shop"), ("advisor", "/advisor"), ("product", "/shop/product/tv-001"), ("cart", "/cart")):
        response = client.get(route)
        assert response.status_code == 200
        (output / f"{name}-en.html").write_text(response.get_data(as_text=True), encoding="utf-8")
    catalogs = json.loads((ROOT / "data/catalogs.json").read_text(encoding="utf-8"))["catalogs"]
    (output / "catalogs.json").write_text(json.dumps(catalogs), encoding="utf-8")
print("Rendered 12 isolated UI fixtures.")
