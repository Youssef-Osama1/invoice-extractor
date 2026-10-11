from fastapi import APIRouter

from app.api.dependencies import InvoiceServiceDep
from app.api.schemas.invoice import InvoiceExtractRequest
from app.schemas.invoice import Invoice

router = APIRouter()


@router.post("/extract")
async def extract_invoice(
    payload: InvoiceExtractRequest, service: InvoiceServiceDep
) -> Invoice:
    return await service.extract(payload.text)
