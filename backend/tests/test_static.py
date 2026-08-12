"""Static SPA serving: the STATIC_DIR-gated fallback (ticket #18).

Behavior is asserted on the existing seam — HTTP against the ASGI app — with a
temp directory standing in for the built frontend. The env var is read inside
create_app, so monkeypatching before entering the client is enough.
"""

from __future__ import annotations

from tests.conftest import api_client

INDEX = "<!doctype html><html><body>SPA</body></html>"


def _write_index(tmp_path) -> None:
    (tmp_path / "index.html").write_text(INDEX, encoding="utf-8")


async def test_root_serves_index_when_static_dir_set(tmp_path, monkeypatch):
    _write_index(tmp_path)
    monkeypatch.setenv("STATIC_DIR", str(tmp_path))
    async with api_client() as client:
        response = await client.get("/")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]
        assert response.text == INDEX


async def test_deep_ui_links_fall_back_to_index(tmp_path, monkeypatch):
    _write_index(tmp_path)
    monkeypatch.setenv("STATIC_DIR", str(tmp_path))
    async with api_client() as client:
        for path in ["/owner", "/types/some-slug/book", "/confirmation"]:
            response = await client.get(path)
            assert response.status_code == 200, path
            assert response.headers["content-type"].startswith("text/html"), path
            assert response.text == INDEX, path


async def test_unknown_api_path_stays_json_error(tmp_path, monkeypatch):
    _write_index(tmp_path)
    monkeypatch.setenv("STATIC_DIR", str(tmp_path))
    async with api_client() as client:
        for path in ["/event-types/nope", "/bookings/nope", "/api/v1/nonexistent"]:
            response = await client.get(path)
            assert response.status_code == 404, path
            assert response.headers["content-type"].startswith("application/json"), path
            body = response.json()
            assert "code" in body, path
            assert "message" in body, path


async def test_api_routes_still_win_when_static_dir_set(tmp_path, monkeypatch):
    _write_index(tmp_path)
    monkeypatch.setenv("STATIC_DIR", str(tmp_path))
    async with api_client() as client:
        response = await client.get("/event-types")
        assert response.status_code == 200
        assert response.headers["content-type"].startswith("application/json")


async def test_unknown_api_path_keeps_contract_semantics(tmp_path, monkeypatch):
    _write_index(tmp_path)
    monkeypatch.setenv("STATIC_DIR", str(tmp_path))
    async with api_client() as client:
        response = await client.get("/event-types/nope/slots")
        assert response.status_code == 404
        assert response.headers["content-type"].startswith("application/json")
        assert response.json()["code"] == "event_type_not_found"


async def test_without_static_dir_app_stays_api_only(tmp_path, monkeypatch):
    monkeypatch.delenv("STATIC_DIR", raising=False)
    async with api_client() as client:
        for path in ["/", "/owner"]:
            response = await client.get(path)
            assert response.status_code == 404, path
            assert response.headers["content-type"].startswith("application/json"), path
        response = await client.get("/event-types")
        assert response.status_code == 200
