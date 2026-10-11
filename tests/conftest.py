from datetime import date

import pytest

from app.config.settings import Settings
from app.schemas.invoice import Invoice, LineItem


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.fixture
def settings():
    return Settings(_env_file=None, llm_api_key="test-key", llm_model="test-model")


@pytest.fixture
def invoice():
    return Invoice(
        is_invoice=True,
        invoice_number="INV-001",
        invoice_date=date(2026, 10, 3),
        due_date=None,
        vendor_name="ACME Office Supplies",
        customer_name="Nile Tech",
        currency="EGP",
        line_items=[
            LineItem(description="A4 Paper", quantity=10, unit_price=150, amount=1500)
        ],
        subtotal=1500,
        tax=210,
        total=1710,
    )
