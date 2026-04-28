from __future__ import annotations

from pathlib import Path
from typing import Iterable

import pandas as pd


BASE_DIR = Path(__file__).resolve().parent
SALES_ROOT = BASE_DIR / "rawdata_Urbaner" / "amazon_sales"
OUTPUT_PATH = BASE_DIR / "output" / "postal_product_sales_summary.csv"


def iter_sales_files() -> Iterable[tuple[str, Path, str]]:
    sources = [
        ("US", SALES_ROOT / "US_sales", "utf-8"),
        ("JP", SALES_ROOT / "JP_sales", "shift-jis"),
    ]

    for market, root, encoding in sources:
        if not root.exists():
            continue
        for path in sorted(root.rglob("*.txt")):
            yield market, path, encoding


def normalize_text(series: pd.Series, placeholder: str) -> pd.Series:
    cleaned = series.astype("string").str.strip()
    cleaned = cleaned.fillna("")
    cleaned = cleaned.replace("", placeholder)
    return cleaned


def coerce_numeric(series: pd.Series) -> pd.Series:
    return pd.to_numeric(series, errors="coerce").fillna(0)


def first_non_empty(series: pd.Series) -> str:
    values = series.astype("string").fillna("").str.strip()
    values = values[values != ""]
    if values.empty:
        return ""
    return values.iloc[0]


def read_sales_file(path: Path, encoding: str) -> pd.DataFrame:
    frame = pd.read_csv(
        path,
        sep="\t",
        encoding=encoding,
        on_bad_lines="skip",
        dtype=str,
        low_memory=False,
    )
    frame.columns = [str(column).strip() for column in frame.columns]
    frame["source_file"] = path.name
    return frame


def build_summary() -> pd.DataFrame:
    frames: list[pd.DataFrame] = []

    for market, path, encoding in iter_sales_files():
        try:
            frame = read_sales_file(path, encoding)
        except Exception as exc:  # pragma: no cover - surfaced to console
            print(f"skip {path}: {exc}")
            continue

        if frame.empty:
            continue

        frame["market"] = market
        frames.append(frame)

    if not frames:
        return pd.DataFrame()

    orders = pd.concat(frames, ignore_index=True)

    if "order-status" not in orders.columns:
        raise KeyError("Missing required column: order-status")

    shipped = orders[orders["order-status"].fillna("").str.strip() == "Shipped"].copy()

    text_placeholders = {
        "ship-city": "(missing city)",
        "ship-state": "(missing state)",
        "ship-postal-code": "(missing postal code)",
        "ship-country": "(missing country)",
        "sku": "(missing sku)",
        "asin": "(missing asin)",
        "product-name": "(missing product name)",
        "currency": "(missing currency)",
        "amazon-order-id": "(missing order id)",
        "market": "(missing market)",
    }

    for column, placeholder in text_placeholders.items():
        if column not in shipped.columns:
            shipped[column] = placeholder
        shipped[column] = normalize_text(shipped[column], placeholder)

    numeric_columns = [
        "quantity",
        "item-price",
        "item-tax",
        "shipping-price",
        "shipping-tax",
        "gift-wrap-price",
        "gift-wrap-tax",
        "item-promotion-discount",
        "ship-promotion-discount",
    ]
    for column in numeric_columns:
        if column not in shipped.columns:
            shipped[column] = 0
        shipped[column] = coerce_numeric(shipped[column])

    if "purchase-date" not in shipped.columns:
        shipped["purchase-date"] = ""
    shipped["purchase-date"] = normalize_text(shipped["purchase-date"], "")

    shipped["line_item_amount"] = shipped["item-price"]
    shipped["gross_order_amount"] = (
        shipped["item-price"]
        + shipped["item-tax"]
        + shipped["shipping-price"]
        + shipped["shipping-tax"]
        + shipped["gift-wrap-price"]
        + shipped["gift-wrap-tax"]
        - shipped["item-promotion-discount"]
        - shipped["ship-promotion-discount"]
    )

    order_level_group = [
        "market",
        "ship-country",
        "ship-postal-code",
        "sku",
        "asin",
        "product-name",
        "amazon-order-id",
        "currency",
    ]

    order_level = (
        shipped.groupby(order_level_group, dropna=False, as_index=False)
        .agg(
            ship_city=("ship-city", first_non_empty),
            ship_state=("ship-state", first_non_empty),
            purchase_date=("purchase-date", first_non_empty),
            quantity=("quantity", "sum"),
            line_item_amount=("line_item_amount", "sum"),
            gross_order_amount=("gross_order_amount", "sum"),
        )
    )

    summary = (
        order_level.groupby(
            ["market", "ship-country", "ship-postal-code", "sku", "asin", "product-name", "currency"],
            dropna=False,
            as_index=False,
        )
        .agg(
            ship_city=("ship_city", first_non_empty),
            ship_state=("ship_state", first_non_empty),
            purchase_times=("amazon-order-id", pd.Series.nunique),
            total_quantity=("quantity", "sum"),
            total_item_amount=("line_item_amount", "sum"),
            total_gross_amount=("gross_order_amount", "sum"),
            first_purchase_date=("purchase_date", lambda s: s[s != ""].min() if (s != "").any() else ""),
            last_purchase_date=("purchase_date", lambda s: s[s != ""].max() if (s != "").any() else ""),
        )
        .sort_values(
            ["market", "ship-country", "ship-postal-code", "sku", "asin", "product-name"],
            kind="stable",
        )
        .reset_index(drop=True)
    )

    summary.insert(0, "source_scope", "shipped_only")
    return summary


def main() -> None:
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    summary = build_summary()
    if summary.empty:
        raise SystemExit("No shipped sales rows were found.")

    summary.to_csv(OUTPUT_PATH, index=False, encoding="utf-8-sig")
    print(f"Wrote {len(summary):,} rows to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()