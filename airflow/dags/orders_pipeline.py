import json
from pathlib import Path

import pandas as pd
import pendulum
from airflow.sdk import dag, task

# from dataclasses import dataclass, asdict
from typing import TypedDict



DATA_DIR = Path("/opt/airflow/data")
RAW_PATH = DATA_DIR / "raw" / "orders.csv"
OUTPUT_PATH = DATA_DIR / "processed" / "orders_summary.json"


class ByCounty(TypedDict):
    country: str
    order_count: int
    total_sales: float


class OrdersPipelineTransformOut(TypedDict):
    paid_orders: int
    total_paid_sales: float
    by_country: list[ByCounty]


@dag(
    schedule=None,
    start_date=pendulum.datetime(2026, 1, 1, tz="UTC"),
    catchup=False,
    tags=["portfolio", "etl"],
)
def orders_pipeline():

    @task
    def extract()-> list[dict]:
        df = pd.read_csv(RAW_PATH)

        return df.to_dict(orient="records")


    @task
    def transform(rows: list[dict]) -> OrdersPipelineTransformOut:
        df = pd.DataFrame(rows)
        paid = df[df["status"] == "paid"]
        number_paid_orders = paid.shape[0]
        total_sales = paid["amount"].sum()

        by_country_list = []
        

        for country, country_sales in paid.groupby("country"):
            by_country = {
                "country": country, 
                "order_count": country_sales.shape[0], 
                "total_sales": country_sales["amount"].sum()
            }
            by_country_list.append(by_country)

        return OrdersPipelineTransformOut(
            paid_orders=number_paid_orders,
            total_paid_sales=total_sales,
            by_country=by_country_list
        )


    @task
    def load(summary: OrdersPipelineTransformOut) -> None:
        OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

        # temporary path to avoid leaving a half writen json file
        temporary_path = OUTPUT_PATH.with_suffix(".tmp")

        temporary_path.write_text(
            json.dumps(summary, indent=2),
            encoding="utf-8",
        )

        temporary_path.replace(OUTPUT_PATH)

        print(f"Wrote summary to {OUTPUT_PATH}")


    rows = extract()
    summary = transform(rows)
    load(summary)

orders_pipeline()
