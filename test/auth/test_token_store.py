from pathlib import Path

from auth.token_store import JsonTokenStore


def test_token_store_save_and_get(tmp_path: Path):
    store = JsonTokenStore(tmp_path / "tok.json")
    token = {"access_token": "a", "token_type": "Bearer"}
    store.save_token(token)
    loaded = store.get_token()
    assert loaded == token


def test_token_store_delete(tmp_path: Path):
    store = JsonTokenStore(tmp_path / "tok.json")
    store.save_token({"access_token": "a"})
    assert store.get_token() is not None
    store.delete_token()
    assert store.get_token() is None


def test_token_store_get_missing_returns_none(tmp_path: Path):
    store = JsonTokenStore(tmp_path / "tok.json")
    assert store.get_token() is None


def test_token_store_handles_corrupt_json(tmp_path: Path):
    path = tmp_path / "tok.json"
    path.write_text("not-json")
    store = JsonTokenStore(path)
    assert store.get_token() is None
