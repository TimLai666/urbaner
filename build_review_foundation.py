"""Build review_foundation.json from attribute_catalog.csv + scored artifacts."""
import json, pandas as pd
from pathlib import Path

OUT_DIR = Path("output/stp_B001K85BN2_B001K85BNC_B008KEJ1LM")
catalog = pd.read_csv("attribute_catalog.csv")

# ── Dimension catalog ─────────────────────────────────────────────────────────
dimension_catalog = []
for _, row in catalog.iterrows():
    families = [f.strip() for f in str(row.get("theory_families","")).split(",") if f.strip()]
    subtheories = [s.strip() for s in str(row.get("theory_subtheories","")).split(",") if s.strip()]
    theory_annotations = {}
    for fam in families:
        theory_annotations[fam] = [s for s in subtheories if s in [
            "attributes","functions","benefits","usage_context_service_experience",
            "physiological","safety","belongingness","esteem","self_actualization",
            "functional","security","relational",
            "altruistic","social_identity","self_enhancement","emotional_expression"
        ]] or subtheories

    dimension_catalog.append({
        "column": row["attribute_key"],
        "label": row["label"],
        "label_zh": row.get("label_zh", ""),
        "theme": row["theme"],
        "attribute_group": row["attribute_group"],
        "salience_column": row["salience_column"],
        "quality_column": row["quality_column"],
        "mention_count": int(row.get("mention_count", 0)),
        "plain_language_definition": row.get("definition", ""),
        "example_review_id": str(row.get("example_review_id", "")),
        "example_quote": str(row.get("example_quote", "")),
        "stat_roles": ["segmentation", "targeting", "positioning"],
        "theory_annotations": theory_annotations,
    })

# ── Theme mapping ─────────────────────────────────────────────────────────────
themes = catalog["theme"].unique().tolist()
theme_mapping = {t: catalog[catalog["theme"]==t]["attribute_key"].tolist() for t in themes}

# ── Attribute extraction summary ──────────────────────────────────────────────
attr_count = len(catalog)
theory_families_used = set()
for _, row in catalog.iterrows():
    for f in str(row.get("theory_families","")).split(","):
        theory_families_used.add(f.strip())

attribute_extraction_summary = {
    "target_minimum": 30,
    "actual_count": attr_count,
    "shortfall_reason": "none — catalog frozen at 114 attributes from prior Urbaner US review corpus",
    "theory_gap": [],
    "themes_discovered": themes,
    "source_corpus": ["B001K85BN2 (398 reviews, JP)", "B001K85BNC (160 reviews, JP)", "B008KEJ1LM (500 reviews, EN)"],
    "scoring_note": "Attribute catalog imported from pre-frozen Urbaner attribute_catalog.csv. Salience scored via keyword matching; quality scored via star-rating + attribute-specific negative-signal adjustment.",
}

# ── People insights ───────────────────────────────────────────────────────────
people_insights = {
    "B001K85BN2": {
        "lang": "Japanese",
        "avg_rating": 3.37,
        "n_reviews": 398,
        "dominant_concerns": [
            "Minimum cut length too long (3mm minimum is a frequent complaint)",
            "Blade sharpness and longevity",
            "Adjustable comb range",
            "Ease of cleaning and maintenance"
        ],
        "frequent_use_context": "Daily beard grooming at home; some users mention travel use"
    },
    "B001K85BNC": {
        "lang": "Japanese",
        "avg_rating": 3.97,
        "n_reviews": 160,
        "dominant_concerns": [
            "Shower/wet use capability positively received",
            "Blade hair pulling occasionally mentioned",
            "Battery type and longevity",
            "Compact and easy to use"
        ],
        "frequent_use_context": "Shower grooming, everyday beard care"
    },
    "B008KEJ1LM": {
        "lang": "English",
        "avg_rating": 3.00,
        "n_reviews": 500,
        "dominant_concerns": [
            "Motor power and cutting performance",
            "Build quality and durability",
            "Value for money",
            "Ease of use and setup"
        ],
        "frequent_use_context": "General beard and mustache grooming; gifting occasion common"
    }
}

# ── Product triggers ──────────────────────────────────────────────────────────
product_triggers = {
    "B001K85BN2": [
        "Users triggered by minimum cut length limitation",
        "Japanese safety and reliability standards drive purchase",
        "Price-to-value ratio key decision factor"
    ],
    "B001K85BNC": [
        "Shower-safe capability is primary trigger",
        "Waterproof rating drives trust and repeat purchase",
        "Compact design for travel"
    ],
    "B008KEJ1LM": [
        "Gifting occasion (husband, father) is major trigger",
        "Value positioning at budget tier",
        "Easy out-of-box experience"
    ]
}

# ── Context scenarios ─────────────────────────────────────────────────────────
context_scenarios = [
    "Daily home beard grooming (all products)",
    "Shower grooming (B001K85BNC strong; B008KEJ1LM moderate)",
    "Travel / business trip portability",
    "Gift purchase for male family member or partner",
    "First-time trimmer buyer seeking easy setup",
    "Detailed mustache / sideburn precision work"
]

# ── System 1 / System 2 split ─────────────────────────────────────────────────
system1_system2_split = {
    "system1_attributes": [
        "compact_size", "color_style_aesthetics", "gift_packaging_quality",
        "product_perceived_premium", "grip_ergonomics", "low_noise_operation",
        "painless_operation", "cut_smoothness"
    ],
    "system2_attributes": [
        "battery_life_duration", "adjustable_comb_settings", "min_cut_length_mm",
        "max_cut_length_mm", "waterproof_rating_ipx8", "blade_sharpness",
        "price_value_ratio", "product_longevity", "motor_power_rpm",
        "num_grooming_functions", "total_attachments_count"
    ],
    "rationale": "System 1 attributes reflect sensory/emotional cues triggered at first touch; System 2 attributes reflect deliberate comparison research before purchase."
}

# ── Maslow keywords ───────────────────────────────────────────────────────────
maslow_keywords = {
    "physiological": ["comfort","pain","grip","ergonomic","weight","noise","vibration"],
    "safety": ["waterproof","IPX8","skin-friendly","rounded tip","safe","no irritation"],
    "belongingness": ["gift","partner","couple","husband","wife","family","share"],
    "esteem": ["professional","premium","stylish","brand","Japanese","quality"],
    "self_actualization": ["versatile","all-in-one","precise","achieve","best","perfect"]
}

# ── Assemble and write ────────────────────────────────────────────────────────
foundation = {
    "dimension_catalog": dimension_catalog,
    "theme_mapping": theme_mapping,
    "attribute_extraction_summary": attribute_extraction_summary,
    "people_insights": people_insights,
    "product_triggers": product_triggers,
    "context_scenarios": context_scenarios,
    "system1_system2_split": system1_system2_split,
    "maslow_keywords": maslow_keywords,
    "scoring_rubric": {
        "salience_axis": "0-7 per review; 0=absent, 7=central focus of review",
        "quality_axis": "0-10 per product per attribute; computed as star-rating proxy adjusted by attribute-specific negative-signal keywords",
        "language_handling": "English (B008KEJ1LM) and Japanese (B001K85BN2, B001K85BNC) keyword sets maintained separately"
    }
}

out_path = OUT_DIR / "review_foundation.json"
with open(out_path, "w", encoding="utf-8") as f:
    json.dump(foundation, f, ensure_ascii=False, indent=2)

print(f"Saved {out_path}")
print(f"  dimension_catalog: {len(dimension_catalog)} attributes")
print(f"  themes: {themes}")
