from __future__ import annotations

import importlib.util
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
from statsmodels.discrete.conditional_models import ConditionalLogit


BASE_DIR = Path(__file__).resolve().parent
REVIEW_DIR = BASE_DIR / "rawdata_Urbaner" / "amazon_reviews" / "001_Beard_Mustache_Trimmers"
CATALOG_PATH = BASE_DIR / "attribute_catalog.csv"
OUTPUT_DIR = BASE_DIR / "output" / "choice_logit_beard_mustache"


SELECTED_ATTRIBUTES = [
    "rechargeable_design",
    "blade_sharpness",
    "blade_hair_pulling",
    "motor_power_rpm",
    "waterproof_rating_ipx8",
    "adjustable_comb_settings",
    "price_value_ratio",
    "ease_of_use_overall",
]

FIT_REVIEW_SAMPLE_SIZE = 2500


def load_scorer_module():
    spec = importlib.util.spec_from_file_location("scorer", str(BASE_DIR / "score_review_attributes.py"))
    if spec is None or spec.loader is None:
        raise RuntimeError("無法載入 score_review_attributes.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_review_files(folder: Path, scorer) -> dict[str, pd.DataFrame]:
    files = sorted(folder.glob("*.xlsx"))
    if not files:
        raise FileNotFoundError(f"找不到評論檔案：{folder}")

    out: dict[str, pd.DataFrame] = {}
    for path in files:
        df = pd.read_excel(path)
        text_col = scorer.pick_text_col(df)
        title_col = scorer.pick_title_col(df)
        df = df.copy()
        df["product"] = path.stem
        df["_text_col"] = text_col
        df["_title_col"] = title_col or ""
        out[path.stem] = df
    return out


def build_attribute_specs(catalog: pd.DataFrame, scorer) -> list[dict[str, object]]:
    specs: list[dict[str, object]] = []
    filtered = catalog[catalog["attribute_key"].isin(SELECTED_ATTRIBUTES)].copy()
    if filtered.empty:
        raise ValueError("attribute_catalog.csv 中找不到選定的分析屬性")

    for _, row in filtered.iterrows():
        specs.append(
            {
                "attribute_key": str(row["attribute_key"]),
                "label": str(row.get("label", row["attribute_key"])),
                "label_zh": str(row.get("label_zh", "")),
                "definition": str(row.get("definition", "")),
                "keywords": scorer.extract_keywords(row),
            }
        )
    return specs


def score_reviews(review_tables: dict[str, pd.DataFrame], attribute_specs: list[dict[str, object]], scorer) -> pd.DataFrame:
    score_rows: list[dict[str, object]] = []

    for product, df in review_tables.items():
        text_col = str(df["_text_col"].iloc[0])
        title_col = str(df["_title_col"].iloc[0]) if "_title_col" in df.columns else ""

        for idx, row in df.reset_index(drop=True).iterrows():
            content = "" if pd.isna(row.get(text_col)) else str(row.get(text_col))
            title = ""
            if title_col and not pd.isna(row.get(title_col)):
                title = str(row.get(title_col))

            review_text = scorer.norm_text(f"{title} {content}")
            if len(review_text) < 8:
                continue

            record: dict[str, object] = {
                "review_id": f"{product}_{idx + 1}",
                "product": product,
                "review_text": content,
                "review_title": title,
                "rating": pd.to_numeric(row.get("星级", np.nan), errors="coerce"),
                "review_date": row.get("评论时间", pd.NaT),
                "country": row.get("所属国家", ""),
                "lang": row.get("语言", ""),
            }

            for spec in attribute_specs:
                hits = scorer.keyword_hit_count(review_text, spec["keywords"])
                record[spec["attribute_key"]] = scorer.hit_to_score(hits)

            score_rows.append(record)

    scores_df = pd.DataFrame(score_rows)
    if scores_df.empty:
        raise ValueError("沒有可用的評論資料可以評分")

    scores_df["review_date"] = pd.to_datetime(scores_df["review_date"], errors="coerce")
    return scores_df


def build_product_profile(scores_df: pd.DataFrame, attribute_specs: list[dict[str, object]]) -> pd.DataFrame:
    attr_cols = [spec["attribute_key"] for spec in attribute_specs]
    profile = scores_df.groupby("product", as_index=False)[attr_cols].mean(numeric_only=True).round(3)
    profile["review_count"] = profile["product"].map(scores_df.groupby("product").size())
    profile["avg_rating"] = profile["product"].map(scores_df.groupby("product")["rating"].mean())
    return profile


def bucket_series(series: pd.Series) -> pd.Series:
    clean = pd.to_numeric(series, errors="coerce")
    clean = clean.fillna(clean.median())
    unique = clean.nunique(dropna=True)

    if unique <= 1:
        return pd.Series(["mid"] * len(clean), index=series.index, dtype="object")

    if unique == 2:
        threshold = clean.median()
        return pd.Series(np.where(clean <= threshold, "low", "high"), index=series.index, dtype="object")

    try:
        buckets = pd.qcut(clean.rank(method="first"), q=3, labels=["low", "mid", "high"])
        return buckets.astype("object")
    except ValueError:
        q1, q2 = clean.quantile([0.33, 0.67]).tolist()
        return pd.Series(
            np.select([clean <= q1, clean <= q2], ["low", "mid"], default="high"),
            index=series.index,
            dtype="object",
        )


def build_product_dummies(profile_df: pd.DataFrame, attribute_specs: list[dict[str, object]]) -> pd.DataFrame:
    profile = profile_df.copy()
    tier_cols = []

    for spec in attribute_specs:
        attr = spec["attribute_key"]
        tier_col = f"{attr}_tier"
        profile[tier_col] = pd.Categorical(
            bucket_series(profile[attr]),
            categories=["low", "mid", "high"],
            ordered=True,
        )
        tier_cols.append(tier_col)

    dummy_df = pd.get_dummies(profile, columns=tier_cols, drop_first=True, dtype=int)
    return dummy_df


def build_choice_long(scores_df: pd.DataFrame, product_features: pd.DataFrame) -> pd.DataFrame:
    review_base = scores_df[["review_id", "product", "rating", "review_date", "country", "lang"]].copy()
    long_df = review_base.merge(product_features, how="cross")
    long_df["choice"] = (long_df["product_x"] == long_df["product_y"]).astype(int)
    long_df = long_df.rename(columns={"product_x": "review_product", "product_y": "alternative_product"})

    feature_cols = [
        col
        for col in long_df.columns
        if any(col.startswith(f"{attr}_tier_") for attr in SELECTED_ATTRIBUTES)
    ]
    keep_cols = ["review_id", "review_product", "alternative_product", "choice", "rating", "review_date", "country", "lang"] + feature_cols
    return long_df[keep_cols].copy()


def fit_conditional_logit(long_df: pd.DataFrame) -> tuple[ConditionalLogit, pd.DataFrame, list[str], int, int, int]:
    review_ids = long_df["review_id"].drop_duplicates().to_numpy()
    if len(review_ids) > FIT_REVIEW_SAMPLE_SIZE:
        rng = np.random.default_rng(42)
        sampled_ids = set(rng.choice(review_ids, size=FIT_REVIEW_SAMPLE_SIZE, replace=False))
        fit_df = long_df[long_df["review_id"].isin(sampled_ids)].copy()
    else:
        fit_df = long_df.copy()

    feature_cols = [
        col
        for col in fit_df.columns
        if col not in {"review_id", "review_product", "alternative_product", "choice", "rating", "review_date", "country", "lang"}
        and fit_df[col].nunique() > 1
    ]
    if not feature_cols:
        raise ValueError("找不到可用的解釋變數")

    exog = fit_df[feature_cols].astype(float)
    endog = fit_df["choice"].astype(int)
    groups = fit_df["review_id"]

    model = ConditionalLogit(endog=endog, exog=exog, groups=groups)
    result = model.fit(method="bfgs", disp=False, maxiter=200)

    terms = list(exog.columns)
    coef_df = pd.DataFrame(
        {
            "term": terms,
            "coefficient": np.asarray(result.params),
            "std_err": np.asarray(result.bse),
            "z_value": np.asarray(result.tvalues),
            "p_value": np.asarray(result.pvalues),
        }
    )
    coef_df["odds_ratio"] = np.exp(coef_df["coefficient"])
    coef_df["direction"] = np.where(coef_df["coefficient"] >= 0, "positive", "negative")
    choice_set_size = int(long_df.groupby("review_id").size().iloc[0])
    return result, coef_df.sort_values("coefficient", ascending=False).reset_index(drop=True), terms, exog.shape[1], choice_set_size, fit_df["review_id"].nunique()


def expected_null_loglik(n_groups: int, choice_set_size: int) -> float:
    return float(n_groups * (-np.log(choice_set_size)))


def build_report(
    scores_df: pd.DataFrame,
    profile_df: pd.DataFrame,
    long_df: pd.DataFrame,
    result,
    coef_df: pd.DataFrame,
    feature_terms: list[str],
    feature_count: int,
    choice_set_size: int,
    fit_review_count: int,
    attribute_specs: list[dict[str, object]],
) -> str:
    n_reviews = scores_df["review_id"].nunique()
    n_products = profile_df["product"].nunique()
    ll_null = expected_null_loglik(n_reviews, choice_set_size)
    pseudo_r2 = 1 - (result.llf / ll_null) if ll_null != 0 else np.nan

    exog = long_df[feature_terms].astype(float)
    predicted_long = long_df[["review_id", "alternative_product", "choice"]].copy()
    predicted_long["utility"] = exog.to_numpy() @ np.asarray(result.params)
    pred_idx = predicted_long.groupby("review_id")["utility"].idxmax()
    predicted = predicted_long.loc[pred_idx, ["review_id", "alternative_product"]].set_index("review_id")["alternative_product"]
    actual = predicted_long.loc[predicted_long["choice"] == 1, ["review_id", "alternative_product"]].set_index("review_id")["alternative_product"]
    hit_rate = predicted.eq(actual).mean()

    lines: list[str] = []
    lines.append("# Choice Logit Report (Detailed)")
    lines.append("")
    lines.append("## 1) Dataset Scope")
    lines.append(f"- Reviews used: {n_reviews:,}")
    lines.append(f"- Products in choice set: {n_products:,}")
    lines.append(f"- Alternatives per choice set: {choice_set_size:,}")
    lines.append(f"- Long-format rows: {len(long_df):,}")
    lines.append(f"- Model features: {feature_count:,}")
    lines.append(f"- Reviews used for fit: {fit_review_count:,}")
    lines.append("")
    lines.append("## 2) Conjoint Workflow (Choice-Based)")
    lines.append("### Step 1. Choice Data Construction")
    lines.append("Each review is treated as one purchase occasion. The reviewed ASIN becomes the chosen alternative; all other products in the category are coded as 0.")
    lines.append("")
    lines.append("### Step 2. Product Attribute Aggregation")
    lines.append("Review-level attribute scores are aggregated into product-level mean profiles, so each product has one comparable feature vector.")
    lines.append("")
    lines.append("### Step 3. Tiering and Dummy Encoding")
    lines.append("Product-level attribute scores are aggregated from review text, then bucketed into low / mid / high tiers and one-hot encoded. Low tier is the reference category.")
    lines.append("")
    lines.append("### Attributes Used (English + Chinese)")
    for spec in attribute_specs:
        label = spec["label_zh"] or spec["label"]
        lines.append(f"- {spec['attribute_key']}: {spec['label']} / {label}")
    lines.append("")
    lines.append("### Step 4. Conditional Logit Estimation")
    lines.append(f"- Log-likelihood: {result.llf:.3f}")
    lines.append(f"- Null log-likelihood: {ll_null:.3f}")
    lines.append(f"- McFadden pseudo R^2: {pseudo_r2:.4f}")
    lines.append(f"- Top-1 hit rate: {hit_rate:.4f}")
    lines.append("")
    lines.append("## 3) Coefficients")
    lines.append("| term | coefficient | std_err | z_value | p_value | odds_ratio | direction |")
    lines.append("|---|---:|---:|---:|---:|---:|---|")
    for _, row in coef_df.iterrows():
        lines.append(
            f"| {row['term']} | {row['coefficient']:.4f} | {row['std_err']:.4f} | {row['z_value']:.3f} | {row['p_value']:.4f} | {row['odds_ratio']:.3f} | {row['direction']} |"
        )
    lines.append("")
    lines.append("## 4) Interpretation")
    lines.append("Positive coefficients increase utility and purchase probability relative to the omitted (low) tier. Negative coefficients reduce utility.")
    lines.append("The coefficient itself is the part-worth utility on the log-odds scale; exponentiating it gives the odds ratio.")
    lines.append("")
    lines.append("## 5) Reporting Notes")
    lines.append("- For business slides, prioritize effects that are both statistically significant and practically large in odds ratio.")
    lines.append("- If willingness-to-pay (WTP) is required, refit with true selling price as an explicit variable.")
    return "\n".join(lines)


def main() -> None:
    warnings.filterwarnings("ignore")
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    scorer = load_scorer_module()
    catalog = pd.read_csv(CATALOG_PATH).fillna("")
    print("Loading review files...", flush=True)
    review_tables = load_review_files(REVIEW_DIR, scorer)
    print("Preparing attribute specs...", flush=True)
    attribute_specs = build_attribute_specs(catalog, scorer)

    print("Scoring reviews...", flush=True)
    scores_df = score_reviews(review_tables, attribute_specs, scorer)
    print("Building product profiles...", flush=True)
    profile_df = build_product_profile(scores_df, attribute_specs)
    print("Encoding product dummies...", flush=True)
    product_features = build_product_dummies(profile_df, attribute_specs)

    score_path = OUTPUT_DIR / "review_attribute_scores.csv"
    profile_path = OUTPUT_DIR / "product_attribute_profile.csv"
    long_path = OUTPUT_DIR / "choice_data_long.csv"
    coef_path = OUTPUT_DIR / "logit_coefficients.csv"
    report_path = OUTPUT_DIR / "choice_logit_report.md"

    scores_df.to_csv(score_path, index=False, encoding="utf-8-sig")
    profile_df.to_csv(profile_path, index=False, encoding="utf-8-sig")

    print("Constructing long choice data...", flush=True)
    long_df = build_choice_long(scores_df, product_features)
    long_df.to_csv(long_path, index=False, encoding="utf-8-sig")

    print("Fitting conditional logit on a sampled review set...", flush=True)
    result, coef_df, feature_terms, feature_count, choice_set_size, fit_review_count = fit_conditional_logit(long_df)
    coef_df.to_csv(coef_path, index=False, encoding="utf-8-sig")

    report = build_report(scores_df, profile_df, long_df, result, coef_df, feature_terms, feature_count, choice_set_size, fit_review_count, attribute_specs)
    report_path.write_text(report, encoding="utf-8")

    print(f"Saved review scores: {score_path}")
    print(f"Saved product profile: {profile_path}")
    print(f"Saved long choice data: {long_path}")
    print(f"Saved coefficients: {coef_path}")
    print(f"Saved report: {report_path}")
    print(f"Log-likelihood: {result.llf:.3f}")
    print(f"McFadden pseudo R^2: {1 - (result.llf / expected_null_loglik(scores_df['review_id'].nunique(), choice_set_size)):.4f}")


if __name__ == "__main__":
    main()