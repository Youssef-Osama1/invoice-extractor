from datetime import date

from pydantic import BaseModel, Field


class LineItem(BaseModel):
    description: str = Field(
        description="Product or service name as written on the invoice"
    )
    quantity: float | None = Field(description="Number of units, null if not stated")
    unit_price: float | None = Field(description="Price per unit, null if not stated")
    amount: float = Field(description="Line total as printed on the invoice")


class Invoice(BaseModel):
    is_invoice: bool = Field(
        description="False if the text is not an invoice or receipt"
    )
    invoice_number: str | None = Field(
        description="Invoice identifier, null if not stated"
    )
    invoice_date: date | None = Field(
        description="Date the invoice was issued, null if not stated"
    )
    due_date: date | None = Field(description="Payment due date, null if not stated")
    vendor_name: str | None = Field(
        description="Company or person that issued the invoice, null if not stated"
    )
    customer_name: str | None = Field(
        description="Company or person being billed, null if not stated"
    )
    currency: str | None = Field(
        description="ISO 4217 currency code such as USD, EUR or EGP, null if not stated"
    )
    line_items: list[LineItem] = Field(
        description="Every billed line in the order it appears"
    )
    subtotal: float | None = Field(description="Total before tax, null if not stated")
    tax: float | None = Field(description="Total tax amount, null if not stated")
    total: float | None = Field(
        description="Final amount due as printed on the invoice, null if not stated"
    )
