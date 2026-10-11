from typing import Annotated

from fastapi import Depends, Request

from app.services.invoice_service import InvoiceService
from app.services.llm_client import LLMClient


def get_llm_client(request: Request) -> LLMClient:
    return request.app.state.llm_client


LLMClientDep = Annotated[LLMClient, Depends(get_llm_client)]


def get_invoice_service(llm_client: LLMClientDep) -> InvoiceService:
    return InvoiceService(llm_client)


InvoiceServiceDep = Annotated[InvoiceService, Depends(get_invoice_service)]
