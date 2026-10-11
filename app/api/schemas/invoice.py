from typing import Annotated

from pydantic import BaseModel, StringConstraints

InvoiceText = Annotated[
    str, StringConstraints(strip_whitespace=True, min_length=1, max_length=20_000)
]


class InvoiceExtractRequest(BaseModel):
    text: InvoiceText
