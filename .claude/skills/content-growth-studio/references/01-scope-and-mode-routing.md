# Scope And Mode Routing

## Purpose

Use this skill as the top-level router for growth-oriented content work that spans:

- article, newsletter, or long-form written content
- long-form video
- short-form video
- social post, thread, or engagement asset

It should combine analysis, generation, packaging, and workflow design in one place, then call other skills only for deeper specialized logic.

## In Scope

- reverse-engineering successful content from artifacts
- content angle and positioning generation
- content topic, niche, and naming ideation
- article and script rewriting
- title, hook, thumbnail concept, CTA, and interaction packaging
- finished draft or script generation
- repurposing one source into multiple channel outputs
- workflow, SOP, batch cadence, and budget planning

## Out Of Scope

- building the landing page or site itself
- pure persona definition with no content deliverable
- pure service design or business model work
- pure quantitative review mining without a content output
- fabrication of analytics, competitor data, or source facts

## Entry Path Detection

Choose `source-led` if the user provides any of:

- URLs
- transcripts
- article text
- existing script
- title plus outline
- competitor examples
- channel examples
- review, support, or social evidence

Choose `brief-led` if the user mostly provides:

- topic or subject
- audience
- channel
- goal
- voice or brand direction
- constraints

If both are present, keep both and treat the source as calibration material for the brief.

## Auto Mode Rules

### `analyze`

Choose when the user wants:

- content formula extraction
- competitor teardown
- hook analysis
- pacing or structure breakdown
- gap identification

### `ideate`

Choose when the user wants:

- niches
- positioning lines
- topic slates
- content series
- channel names
- angle sets

### `rewrite`

Choose when the user provides a draft and wants:

- stronger opening
- better flow
- better readability
- stronger sharing impulse
- clearer CTA

### `package`

Choose when the user mainly wants:

- titles
- hooks
- thumbnail concepts
- CTA options
- poll prompts
- comment prompts
- share prompts

### `produce`

Choose when the user wants:

- a full article
- a full long-form video script
- a short-form script
- social cutdowns
- cross-channel repurposing

### `system`

Choose when the user wants:

- publishing workflow
- 3-hour SOP
- tool stack
- prompt stack
- monthly plan
- batch production design
- budget breakdown

## Boundary Rules

- If the user asks to design or code a landing page, route to `landing-page-studio` for the page artifact. Keep this skill for the messaging package only.
- If the user only needs persona or audience clarification, route to `customer-persona-framer`.
- If the user needs a psychology-first funnel strategy, route to `sor-marketing-strategy`.
- If the user needs deep trigger or CTA framing, route to `psychological-trigger-marketing` and `maslow-five-needs-marketing`.
- If the user mainly needs structured ideation expansion, route to `scamper`.
- If the user provides review-like corpora and asks for evidence-backed segmentation or theory coding, route upstream to `review-mining-stp` and the theory-analysis skills before packaging the final content direction.

## Final Ownership Rule

This skill owns:

- entry-path detection
- mode detection
- channel framing
- assumptions handling
- final assembly

It does not try to replace the deeper logic already owned by specialist skills.
