import logging

from app.prompts.invoice import INVOICE_SYSTEM_PROMPT, build_invoice_prompt
from app.schemas.invoice import Invoice
from app.services.llm_client import LLMClient

logger = logging.getLogger(__name__)

TOTALS_TOLERANCE = 0.01


class InvoiceService:
    def __init__(self, llm_client: LLMClient) -> None:
        self._llm_client = llm_client

    async def extract(self, invoice_text: str) -> Invoice:
        invoice = await self._llm_client.extract(
            prompt=build_invoice_prompt(invoice_text),
            schema=Invoice,
            system=INVOICE_SYSTEM_PROMPT,
        )
        self._check_totals(invoice)
        return invoice

    def _check_totals(self, invoice: Invoice) -> None:
        if invoice.subtotal is None or invoice.tax is None:
            return

        expected = invoice.subtotal + invoice.tax
        if abs(expected - invoice.total) > TOTALS_TOLERANCE:
            logger.warning(
                "Totals mismatch: invoice=%s subtotal=%s tax=%s total=%s",
                invoice.invoice_number,
                invoice.subtotal,
                invoice.tax,
                invoice.total,
            )
