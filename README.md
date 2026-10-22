# Invoice Extractor

[![CI](https://github.com/Youssef-Osama1/invoice-extractor/actions/workflows/ci.yml/badge.svg)](https://github.com/Youssef-Osama1/invoice-extractor/actions/workflows/ci.yml)

Extract structured data from invoices with an LLM.

Send the text of an invoice or receipt and get back vendor, dates, currency,
line items and totals as validated JSON. Text that is not an invoice is rejected.

## Quick Start

```bash
uv sync
cp .env.example .env    # add your LLM_API_KEY
uv run uvicorn app.main:app --reload
```

API docs at http://localhost:8000/docs.

## Usage

```bash
curl -X POST http://localhost:8000/invoices/extract \
  -H "Content-Type: application/json" \
  -d '{"text": "ACME Ltd.\nInvoice #42\nPaper x2  30.00\nTotal EUR 30.00"}'
```

| Status | Meaning |
|--------|---------|
| 200 | Extracted invoice |
| 422 | Empty or too long text, or the text is not an invoice |
| 502 | The model returned output that does not match the schema |

## Development

```bash
uv run pytest                                        # tests, no network access
uv run python -m evals.run_invoice                   # evals against the real model
uv run --env-file .env python playground/first_call.py
```

The evals run every case in `evals/invoice_cases.jsonl` three times and print
accuracy per field. Run them after changing the prompt, the schema or the model.

## Docker

```bash
docker build -f docker/Dockerfile -t invoice-extractor .
docker run --rm -p 8000:8000 --env-file .env invoice-extractor
```

The image installs runtime dependencies only, runs as a non-root user and
listens on `$PORT` (default 8000). `.env` is never copied into the image, so
secrets are passed at run time. Values in `.env` must not be quoted for
`--env-file`.

## CI and Deployment

Every push to `main` and every pull request runs
`.github/workflows/ci.yml`: ruff lint, ruff format check, pytest and a
Docker build.

The app runs on Render as a Docker web service:

| Setting | Value |
|---|---|
| Dockerfile path | `./docker/Dockerfile` |
| Build context | `.` |
| Health check path | `/health` |
| Auto-deploy | After CI checks pass |
| Environment | `LLM_API_KEY` (other settings have defaults) |

## Project Structure

```text
├── .github/          # CI workflow
├── app/
│   ├── api/          # Routes, dependencies and request/response models
│   ├── config/       # Settings loaded from .env
│   ├── core/         # Logging and exceptions
│   ├── prompts/      # System prompts
│   ├── schemas/      # Pydantic models the LLM fills in
│   ├── services/     # LLM client and business logic
│   └── main.py       # FastAPI app entry point
├── docker/           # Dockerfile
├── docs/             # Documentation files
├── evals/            # Eval cases and runner for output quality
├── playground/       # Experimental code, never imported by app/
├── tests/            # Tests that run without network access
├── .env.example      # Environment variables template
├── pyproject.toml    # Project dependencies and metadata
└── uv.lock           # Locked dependencies
```
