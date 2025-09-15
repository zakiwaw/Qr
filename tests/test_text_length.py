import sys
import asyncio
import pathlib
import pytest

# Add backend directory to path for importing server module
backend_path = pathlib.Path(__file__).resolve().parent.parent / 'backend'
sys.path.append(str(backend_path))

import server  # type: ignore


class DummyCollection:
    async def insert_one(self, doc):
        return None


def patch_db(monkeypatch):
    dummy_db = type('DummyDB', (), {'barcodes': DummyCollection()})()
    monkeypatch.setattr(server, 'db', dummy_db)


def test_generate_barcode_too_long(monkeypatch):
    patch_db(monkeypatch)
    long_text = 'a' * 256
    request = server.BarcodeRequest(text=long_text)
    with pytest.raises(server.HTTPException) as exc:
        asyncio.run(server.generate_barcode(request))
    assert exc.value.status_code == 400
    assert '255' in exc.value.detail


def test_generate_barcode_max_length(monkeypatch):
    patch_db(monkeypatch)
    monkeypatch.setattr(server, 'generate_barcode_image', lambda text: 'image')
    valid_text = 'a' * 255
    request = server.BarcodeRequest(text=valid_text)
    response = asyncio.run(server.generate_barcode(request))
    assert response.text == valid_text
