import asyncio

from app.config.settings import get_settings
from app.schemas.invoice import Invoice
from app.services.llm_client import LLMClient

SAMPLE_INVOICE = """
ACME Office Supplies Ltd.
12 Tahrir Street, Cairo

INVOICE #INV-2026-0042
Date: 3 October 2026
Due: 2 November 2026

Bill to: Nile Tech Solutions

Description              Qty   Unit Price   Amount
A4 Paper (box)            10       150.00   1,500.00
Ink Cartridge Black        4       425.00   1,700.00
Desk Organizer             2       210.00     420.00

Subtotal                                    3,620.00
VAT 14%                                       506.80
Total Due                               EGP 4,126.80
"""


async def main() -> None:
    client = LLMClient(get_settings())
    try:
        invoice = await client.extract(
            prompt=SAMPLE_INVOICE,
            schema=Invoice,
            system="Extract the invoice data.",
        )
        print(invoice.model_dump_json(indent=2))
        print(type(invoice.invoice_date))
    finally:
        await client.close()


asyncio.run(main())
