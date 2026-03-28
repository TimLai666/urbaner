MODULE_SEQUENCE = [
    "review-foundation",
    "segmentation-variables",
    "segment-clustering",
    "segment-profiles",
    "current-target-market",
    "potential-target-market",
    "target-selection",
    "positioning-scorecard",
    "perceptual-map",
    "positioning-diagnostics",
    "strategy-matrix",
]

RUN_MODE_MODULES = {
    "full": MODULE_SEQUENCE,
    "segmentation": [
        "review-foundation",
        "segmentation-variables",
        "segment-clustering",
        "segment-profiles",
    ],
    "targeting": [
        "current-target-market",
        "potential-target-market",
        "target-selection",
    ],
    "positioning": [
        "positioning-scorecard",
        "perceptual-map",
        "positioning-diagnostics",
        "strategy-matrix",
    ],
}

ALLOWED_CUSTOM_MODULES = set(MODULE_SEQUENCE)
