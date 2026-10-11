import logging
from unittest.mock import AsyncMock

import pytest

from app.core.exceptions import NotAnInvoiceError
from app.prompts.invoice import INVOICE_SYSTEM_PROMPT
from app.schemas.invoice import Invoice
from app.services.invoice_service import InvoiceService
from app.services.llm_client import LLMClient

pytestmark = pytest.mark.anyio


@pytest.fixture
def llm_client(invoice):
    client = AsyncMock(spec=LLMClient)
    client.extract.return_value = invoice
    return client


@pytest.fixture
def service(llm_client):
    return InvoiceService(llm_client)


async def test_extract_returns_the_model_invoice(service, invoice):
    assert await service.extract("some invoice") == invoice


async def test_extract_wraps_text_and_sends_schema(service, llm_client):
    await service.extract("  some invoice  ")

    llm_client.extract.assert_awaited_once_with(
        prompt="<invoice>\nsome invoice\n</invoice>",
        schema=Invoice,
        system=INVOICE_SYSTEM_PROMPT,
    )


async def test_extract_rejects_non_invoice(service, llm_client, invoice):
    llm_client.extract.return_value = invoice.model_copy(update={"is_invoice": False})

    with pytest.raises(NotAnInvoiceError):
        await service.extract("hello")


async def test_totals_mismatch_logs_warning(service, llm_client, invoice, caplog):
    llm_client.extract.return_value = invoice.model_copy(update={"total": 9999})

    with caplog.at_level(logging.WARNING):
        await service.extract("some invoice")

    assert "Totals mismatch" in caplog.text


async def test_matching_totals_log_nothing(service, caplog):
    with caplog.at_level(logging.WARNING):
        await service.extract("some invoice")

    assert caplog.text == ""


async def test_missing_total_skips_check(service, llm_client, invoice, caplog):
    llm_client.extract.return_value = invoice.model_copy(update={"total": None})

    with caplog.at_level(logging.WARNING):
        await service.extract("some invoice")

    assert caplog.text == ""
