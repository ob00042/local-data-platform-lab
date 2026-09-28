import os
from pathlib import Path

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

PROCESSED_DATA_PATH = "data/processed"
PROCESSED_SUMMARY = "orders_summary.json"


class CountrySummary(BaseModel):
    country: str
    order_count: int
    total_sales: float


class OrdersSummary(BaseModel):
    paid_orders: int
    total_paid_sales: float
    by_country: list[CountrySummary]


app = FastAPI(title="Orders Summary API", version="0.1.0")


@app.get("/health")
async def root() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/summary", response_model=OrdersSummary)
async def summary() -> OrdersSummary:
    processed_summary_path = Path(PROCESSED_DATA_PATH) / PROCESSED_SUMMARY

    if not os.path.exists(processed_summary_path):
        raise HTTPException(status_code=404, detail="Processed summary does not exist")

    summary = OrdersSummary.model_validate_json(processed_summary_path.read_text(encoding="utf-8"))

    return summary
