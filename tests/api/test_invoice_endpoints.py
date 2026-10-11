from unittest.mock import AsyncMock

import pytest
from fastapi.testclient import TestClient

from app.api.dependencies import get_invoice_service
from app.core.exceptions import LLMOutputError, NotAnInvoiceError
from app.main import app
from app.services.invoice_service import InvoiceService


@pytest.fixture
def service(invoice):
    fake = AsyncMock(spec=InvoiceService)
    fake.extract.return_value = invoice
    app.dependency_overrides[get_invoice_service] = lambda: fake
    yield fake
    app.dependency_overrides.clear()


@pytest.fixture
def client():
    return TestClient(app)


def test_extract_returns_invoice(client, service, invoice):
    response = client.post("/invoices/extract", json={"text": "some invoice"})

    assert response.status_code == 200
    assert response.json() == invoice.model_dump(mode="json")
    service.extract.assert_awaited_once_with("some invoice")


def test_blank_text_is_rejected_before_the_service(client, service):
    response = client.post("/invoices/extract", json={"text": "   "})

    assert response.status_code == 422
    service.extract.assert_not_awaited()


def test_too_long_text_is_rejected(client, service):
    response = client.post("/invoices/extract", json={"text": "x" * 20_001})

    assert response.status_code == 422
    service.extract.assert_not_awaited()


def test_non_invoice_returns_422(client, service):
    service.extract.side_effect = NotAnInvoiceError("not an invoice")

    response = client.post("/invoices/extract", json={"text": "hello"})

    assert response.status_code == 422
    assert response.json() == {"detail": "not an invoice"}


def test_bad_model_output_returns_502(client, service):
    service.extract.side_effect = LLMOutputError("did not match Invoice")

    response = client.post("/invoices/extract", json={"text": "some invoice"})

    assert response.status_code == 502
    assert response.json() == {"detail": "did not match Invoice"}
