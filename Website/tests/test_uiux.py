"""UI/UX regression checks. No real account data or external services are used."""
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit
import re
import pytest
from app import ROOT, RELEASE
from i18n import translations
from test_site import app, client, user, login_as, post


class Markup(HTMLParser):
    def __init__(self, text):
        super().__init__(convert_charrefs=True)
        self.tags = []
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        self.tags.append((tag, dict(attrs)))


@pytest.mark.parametrize("language", ["en", "ar"])
@pytest.mark.parametrize("path", ["/", "/login", "/register", "/contact"])
def test_new_public_markup(client, language, path):
    with client.session_transaction() as session:
        session["language"] = language
    response = client.get(path)
    assert response.status_code == 200
    markup = Markup(response.get_data(as_text=True))
    ids = [a["id"] for _, a in markup.tags if "id" in a]
    assert len(ids) == len(set(ids))
    assert "nav-menu" in ids and "nav-toggle" in ids
    assert "back-to-top" in ids
    assert any(a.get("href", "").startswith("/static/css/experience.css") for _, a in markup.tags)
    for tag, attrs in markup.tags:
        if tag == "img":
            assert "alt" in attrs and "width" in attrs and "height" in attrs
        if tag == "button":
            assert attrs.get("aria-label") or not attrs.get("class") == "icon-button"


@pytest.mark.parametrize("language", ["en", "ar"])
@pytest.mark.parametrize("path", ["/shop", "/advisor", "/membership", "/cart", "/settings", "/shop/product/tv-001"])
def test_authenticated_markup_and_assets(app, client, language, path):
    login_as(client, user(app))
    with client.session_transaction() as session:
        session["language"] = language
    response = client.get(path)
    assert response.status_code == 200
    markup = Markup(response.get_data(as_text=True))
    ids = [a["id"] for _, a in markup.tags if "id" in a]
    assert len(ids) == len(set(ids))
    for tag, attrs in markup.tags:
        target = attrs.get("src", "") if tag in ("img", "script") else attrs.get("href", "") if tag == "link" else ""
        if target.startswith("/static/"):
            assert client.get(target).status_code == 200, target


def test_catalog_controls_have_labels_and_private_links(app, client):
    home = client.get("/").get_data(as_text=True)
    assert "data-add-cart" not in home and 'id="shop-search"' not in home
    assert "/login?next=/shop/product/tv-001" in home
    assert "/login?next=/shop?category%3Dboards" in home
    login_as(client, user(app))
    body = client.get("/shop").get_data(as_text=True)
    markup = Markup(body)
    ids = {a.get("id") for _, a in markup.tags}
    assert {"shop-search", "shop-sort", "clear-search", "active-category", "catalog-status", "collection-title"} <= ids
    assert body.count("data-catalog-view=") == 2
    assert 'id="catalog-status"' in body and 'aria-atomic="true"' in body
    assert "results-count" not in body


def test_new_translation_keys_cover_both_languages():
    required = {
        "catalog_title", "catalog_sort", "catalog_view_grid", "catalog_view_list",
        "catalog_search_clear", "catalog_filter_remove", "guide_open_models",
        "guide_step_model", "guide_step_code", "guide_step_result",
        "account_form_required", "account_password_match", "footer_tagline",
        "contact_short", "contact_form_title", "back_to_top",
    }
    for language in ("en", "ar"):
        for key in required:
            assert translations[language].get(key) not in (None, "", key)


def test_failed_contact_form_retains_submitted_values(client):
    result = post(client, "/contact", {
        "full_name": "UI Test", "phone": "+96171234567",
        "email": "invalid-email", "message": "Retain my message.", "topic": "solar",
    })
    assert result.status_code == 200
    body = result.get_data(as_text=True)
    assert 'value="UI Test"' in body and 'value="invalid-email"' in body
    assert "Retain my message.</textarea>" in body
    assert 'value="solar" selected' in body


def test_theme_and_asset_cache_revision(client):
    body = client.get("/").get_data(as_text=True)
    assert f"experience.css?v={RELEASE}" in body and f"workbench.css?v={RELEASE}" in body
    response = client.get("/static/css/experience.css")
    assert response.status_code == 200
    assert "prefers-reduced-motion" in response.get_data(as_text=True)
    assert "style-src 'self'" in client.get("/").headers["Content-Security-Policy"]


def test_launchers_and_no_external_interface_dependencies():
    assert (ROOT.parent / "START_WINDOWS.bat").is_file()
    launcher = (ROOT.parent / "START_WINDOWS.bat").read_text(encoding="utf-8")
    assert 'cd /d "%~dp0Website"' in launcher
    assert '.venv\\Scripts\\python.exe' in launcher
    css = (ROOT / "static/css/experience.css").read_text(encoding="utf-8")
    assert "@import" not in css
    assert "fonts.googleapis.com" not in css
