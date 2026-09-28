import json

from fastapi.testclient import TestClient

import app.main as main

client = TestClient(main.app)


def test_health() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_summary(tmp_path, monkeypatch) -> None:
    summary_name = "orders_summary.json"
    summary_path = tmp_path / summary_name

    summary = {
        "paid_orders": 7,
        "total_paid_sales": 840.5,
        "by_country": [
            {
                "country": "GR",
                "order_count": 1,
                "total_sales": 120.5,
            }
        ],
    }

    summary_path.write_text(
        json.dumps(summary),
        encoding="utf-8",
    )

    monkeypatch.setattr(
        main,
        "PROCESSED_DATA_PATH",
        tmp_path,
    )

    monkeypatch.setattr(main, "PROCESSED_SUMMARY", summary_name)

    response = client.get("/summary")
    assert response.status_code == 200

    body = response.json()

    assert body["paid_orders"] == 7
    assert body["total_paid_sales"] == 840.5


def test_summary_no_file(tmp_path, monkeypatch) -> None:
    summary_name = "no_file.json"

    monkeypatch.setattr(
        main,
        "PROCESSED_DATA_PATH",
        tmp_path,
    )

    monkeypatch.setattr(main, "PROCESSED_SUMMARY", summary_name)

    response = client.get("/summary")

    assert response.status_code == 404
    data = response.json()
    assert data["detail"] == "Processed summary does not exist"
