import asyncio
from collections import defaultdict
from pathlib import Path
from typing import Any

from pydantic import BaseModel

from app.config.settings import get_settings
from app.core.exceptions import LLMOutputError, NotAnInvoiceError
from app.services.invoice_service import InvoiceService
from app.services.llm_client import LLMClient

CASES_PATH = Path(__file__).parent / "invoice_cases.jsonl"
REPEATS = 3
MAX_CONCURRENCY = 2
MAX_RETRIES = 10
AMOUNT_TOLERANCE = 0.01


class EvalCase(BaseModel):
    id: str
    text: str
    expected: dict[str, Any]


def load_cases() -> list[EvalCase]:
    lines = CASES_PATH.read_text(encoding="utf-8").splitlines()
    return [EvalCase.model_validate_json(line) for line in lines if line.strip()]


async def predict(service: InvoiceService, text: str) -> dict[str, Any]:
    try:
        invoice = await service.extract(text)
    except NotAnInvoiceError:
        return {"is_invoice": False}
    except LLMOutputError as error:
        return {"error": str(error)}

    predicted = invoice.model_dump(mode="json")
    predicted["line_item_count"] = len(invoice.line_items)
    return predicted


def matches(expected: Any, actual: Any) -> bool:
    if isinstance(expected, float) and isinstance(actual, int | float):
        return abs(expected - actual) <= AMOUNT_TOLERANCE
    if isinstance(expected, str) and isinstance(actual, str):
        return expected.casefold().strip() == actual.casefold().strip()
    return expected == actual


async def main() -> None:
    cases = load_cases()
    settings = get_settings().model_copy(update={"llm_max_retries": MAX_RETRIES})
    client = LLMClient(settings)
    service = InvoiceService(client)
    semaphore = asyncio.Semaphore(MAX_CONCURRENCY)

    async def run(case: EvalCase) -> tuple[EvalCase, dict[str, Any]]:
        async with semaphore:
            return case, await predict(service, case.text)

    try:
        results = await asyncio.gather(
            *(run(case) for case in cases for _ in range(REPEATS))
        )
    finally:
        await client.close()

    hits: dict[str, int] = defaultdict(int)
    totals: dict[str, int] = defaultdict(int)
    for case, predicted in results:
        for field, expected in case.expected.items():
            totals[field] += 1
            actual = predicted.get(field)
            if matches(expected, actual):
                hits[field] += 1
            else:
                print(f"[{case.id}] {field}: expected {expected!r}, got {actual!r}")

    print(f"\n{len(cases)} cases x {REPEATS} runs")
    for field, total in totals.items():
        print(f"{field:<16} {hits[field]}/{total}  {hits[field] / total:.0%}")


if __name__ == "__main__":
    asyncio.run(main())
