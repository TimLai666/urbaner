# Handoff Matrix

## Rule

This skill keeps ownership of routing, scope control, and final assembly.
Use the skills below when the task needs deeper logic than this umbrella skill should carry.

| Skill | Use when | Typical handoff payload | Expected return |
| --- | --- | --- | --- |
| `human-writing` | Final prose needs naturalization, tone cleanup, or human-facing polish | draft, audience, tone goal, keep-or-change rules | polished prose |
| `psychological-trigger-marketing` | Need stronger hooks, angle stacks, CTA psychology, curiosity, urgency, or trigger framing | offer/content topic, audience, channel, conversion goal | trigger directions, hook ideas, CTA set |
| `maslow-five-needs-marketing` | Need identity, belonging, aspiration, layered emotion, or shareability framing | audience, offer/topic, desired emotion, channel | emotional message layers, CTA directions |
| `scamper` | Need structured topic expansion or angle generation | target topic, innovation goal, constraints | expanded angle set |
| `customer-persona-framer` | Audience is unclear, underdefined, or conflicting | product/topic, audience clues, usage context | persona or journey-framing block |
| `sor-marketing-strategy` | The task is strategy-first, funnel-first, or behavior-design-first | brand or offer, audience, channel context, goal | message strategy brief, psychology map, KPI direction |
| `theory-analysis-product-positioning` | Need stronger positioning line, attribute-benefit framing, or usage-context angle | evidence items, analysis goal | theory-coded positioning insights |
| `review-mining-stp` | The user provides review-like corpora and wants evidence-backed segmentation before content generation | scored or prepared review artifacts, goal | segment insights and evidence-backed framing |
| `theory-analysis-purchase-motivation` | Need evidence-backed motivation coding from mixed evidence | evidence items, analysis goal | coded motivations |
| `theory-analysis-wom-motivation` | Need evidence-backed sharing or WOM motive coding | evidence items, analysis goal | coded WOM motives |

## Boundary Reminder

- Do not route every title or CTA request out to specialist skills by default.
- Use specialist skills when the request is deep enough that their domain logic materially improves the answer.
- Reassemble specialist outputs into one channel-ready final response instead of dumping disconnected sub-results.

## Landing Page Boundary

If the user wants the actual landing page artifact, route the page build to `landing-page-studio`.
Use this skill only for upstream or adjacent content work such as:

- messaging package
- title and hook set
- section angle ideas
- CTA variants
- repurposed promo assets
