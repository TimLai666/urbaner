"""
build_stacked_data.py

Convert raw purchase / choice records into the stacked observation table required
for logistic conjoint analysis.

Input:
    - card_definitions: a DataFrame where each row is a product card with its
      attribute encoding. Must have a column 'card_id'.
    - purchase_records: a DataFrame where each row is one customer-purchase event,
      with columns 'customer_id' and 'card_id' (the card they actually purchased).

Output:
    - stacked: long-format DataFrame with columns from card_definitions plus
      'customer_id' and 'y' (1 if this card was the one purchased, 0 otherwise).

Each customer contributes M rows, where M = number of cards. Total rows = N × M.

Assumption: every customer's consideration set covers all M cards. This is the
default in revealed-preference conjoint when actual consideration data is
unavailable. If consideration sets vary per customer, supply them as an extra
'considered_cards' list per customer and filter accordingly — see the
ConsiderationSetExpander class below.
"""

from __future__ import annotations
import pandas as pd
from typing import Iterable


def build_stacked_data(
    card_definitions: pd.DataFrame,
    purchase_records: pd.DataFrame,
    card_id_col: str = "card_id",
    customer_id_col: str = "customer_id",
    consideration_set_col: str | None = None,
) -> pd.DataFrame:
    """
    Build the stacked observation table for logistic conjoint.

    Parameters
    ----------
    card_definitions : pd.DataFrame
        One row per product card. Must include a card_id column and the encoded
        attribute columns.
    purchase_records : pd.DataFrame
        One row per customer purchase. Must include customer_id and card_id.
    card_id_col : str
        Name of the card identifier column.
    customer_id_col : str
        Name of the customer identifier column.
    consideration_set_col : str, optional
        If provided, the column in purchase_records containing each customer's
        considered card list. If None (default), every customer is assumed to
        have considered all cards.

    Returns
    -------
    pd.DataFrame
        Long-format stacked table with columns:
            customer_id, card_id, <all attribute columns>, y
    """
    if card_id_col not in card_definitions.columns:
        raise ValueError(f"card_definitions must have column '{card_id_col}'")
    if customer_id_col not in purchase_records.columns:
        raise ValueError(f"purchase_records must have column '{customer_id_col}'")
    if card_id_col not in purchase_records.columns:
        raise ValueError(f"purchase_records must have column '{card_id_col}'")

    rows = []
    for _, prow in purchase_records.iterrows():
        customer = prow[customer_id_col]
        chosen_card = prow[card_id_col]

        if consideration_set_col is not None:
            considered = prow[consideration_set_col]
        else:
            considered = card_definitions[card_id_col].tolist()

        for cid in considered:
            card_row = card_definitions.loc[
                card_definitions[card_id_col] == cid
            ].iloc[0].to_dict()
            card_row[customer_id_col] = customer
            card_row["y"] = 1 if cid == chosen_card else 0
            rows.append(card_row)

    stacked = pd.DataFrame(rows)
    # Reorder columns: customer_id, card_id, attributes..., y
    attr_cols = [c for c in card_definitions.columns if c != card_id_col]
    cols = [customer_id_col, card_id_col] + attr_cols + ["y"]
    stacked = stacked[cols]
    return stacked


def validate_stacked(stacked: pd.DataFrame, customer_id_col: str = "customer_id") -> dict:
    """
    Sanity-check a stacked dataset.

    Returns a dict with diagnostics. Issues a warning if anything looks off.
    """
    diagnostics = {}
    diagnostics["total_rows"] = len(stacked)
    diagnostics["unique_customers"] = stacked[customer_id_col].nunique()
    diagnostics["mean_choices_per_customer"] = (
        stacked.groupby(customer_id_col)["y"].sum().mean()
    )
    diagnostics["positive_rate"] = stacked["y"].mean()

    if diagnostics["mean_choices_per_customer"] != 1.0:
        print(
            f"⚠ Each customer should have exactly 1 chosen card. "
            f"Got mean={diagnostics['mean_choices_per_customer']:.2f}"
        )

    if diagnostics["total_rows"] < 50:
        print("⚠ Sample size is very small (< 50 stacked observations). "
              "Treat results as directional only.")

    return diagnostics


# ----------------------------------------------------------------------------
# Demo with the case-study data
# ----------------------------------------------------------------------------
if __name__ == "__main__":
    # 8 product cards from the safety-glasses case study
    cards = pd.DataFrame([
        # card_id, UKNOW, MORKSUKY, price, pink, purple, size_145, size_162, anti_scratch, uv_protection
        {"card_id": 1, "UKNOW": 0, "MORKSUKY": 0, "price": 15.99, "pink": 0, "purple": 0, "size_145": 0, "size_162": 0, "anti_scratch": 1, "uv_protection": 1},
        {"card_id": 2, "UKNOW": 0, "MORKSUKY": 0, "price": 15.99, "pink": 1, "purple": 0, "size_145": 0, "size_162": 0, "anti_scratch": 1, "uv_protection": 1},
        {"card_id": 3, "UKNOW": 1, "MORKSUKY": 0, "price": 13.98, "pink": 0, "purple": 0, "size_145": 0, "size_162": 1, "anti_scratch": 0, "uv_protection": 1},
        {"card_id": 4, "UKNOW": 1, "MORKSUKY": 0, "price": 13.98, "pink": 1, "purple": 0, "size_145": 0, "size_162": 1, "anti_scratch": 0, "uv_protection": 1},
        {"card_id": 5, "UKNOW": 1, "MORKSUKY": 0, "price": 13.98, "pink": 0, "purple": 1, "size_145": 0, "size_162": 1, "anti_scratch": 0, "uv_protection": 1},
        {"card_id": 6, "UKNOW": 0, "MORKSUKY": 1, "price": 14.95, "pink": 0, "purple": 0, "size_145": 1, "size_162": 0, "anti_scratch": 1, "uv_protection": 0},
        {"card_id": 7, "UKNOW": 0, "MORKSUKY": 1, "price": 14.95, "pink": 1, "purple": 0, "size_145": 1, "size_162": 0, "anti_scratch": 1, "uv_protection": 0},
        {"card_id": 8, "UKNOW": 0, "MORKSUKY": 1, "price": 14.95, "pink": 0, "purple": 1, "size_145": 1, "size_162": 0, "anti_scratch": 1, "uv_protection": 0},
    ])

    # Mock 20 customers' purchase records
    purchases = pd.DataFrame([
        {"customer_id": i+1, "card_id": (i % 8) + 1} for i in range(20)
    ])

    stacked = build_stacked_data(cards, purchases)
    print(stacked.head(10))
    print()
    print("Diagnostics:", validate_stacked(stacked))
    print(f"\nFinal shape: {stacked.shape}  (expected: 20 × 8 = 160 rows)")
