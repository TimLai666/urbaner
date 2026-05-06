# Source Analysis Playbook

## Purpose

Use this playbook in `analyze` mode and in any `rewrite` or `produce` task that starts from existing material.

## Step 1: Normalize The Source Set

Turn the raw inputs into a compact source inventory:

- what the source is
- what channel it belongs to
- what promise it appears to make
- whether it is primary material or competitor/reference material

If multiple sources conflict, prefer:

1. direct user-owned draft
2. transcript or pasted content
3. notes or summary
4. inaccessible URL guesswork never

## Step 2: Extract The Core Promise

For each source, identify:

- the audience it seems to speak to
- the payoff it promises
- the pain, curiosity, aspiration, or identity it activates
- the channel fit

## Step 3: Analyze The Delivery System

Reverse-engineer these dimensions:

- `premise`: the main claim or framing
- `hook`: how attention is captured
- `structure`: section order and logic
- `pacing`: where the speed changes
- `tone`: authority, intimacy, urgency, or entertainment level
- `proof`: examples, specificity, contrast, or credibility devices
- `retention_share_drivers`: what keeps people reading or watching
- `cta_behavior`: what action the content pushes at the end

## Step 4: Identify Reusable Patterns

Condense patterns into reusable rules such as:

- opening formula
- section rhythm
- curiosity loops
- identity reinforcement
- visual or screenshot moments
- CTA timing

Do not stop at "it sounds engaging". Convert observations into transferable rules.

## Step 5: Identify Gaps

Look for:

- overused angles
- audience segments not being served
- unclaimed positioning
- weak proof
- generic hooks
- flat endings
- weak packaging relative to content quality

## Source-Specific Notes

### URLs

- Analyze only if the content is actually accessible.
- If the link is inaccessible, ask for transcript, excerpts, notes, or screenshots.

### Transcripts

- Treat transcript quality as the best structural source for spoken content.
- Preserve spoken cadence only when it helps the target output.

### Article Text

- Look closely at title, lead, section transitions, and final CTA.

### Existing Script

- Separate spoken beats from visual beats.
- Identify where viewer attention likely drops.

### Competitor Or Channel Examples

- Extract patterns.
- Do not invent weaknesses that were not observed.

### Review Or Social Evidence

- Use evidence to sharpen angle, benefit framing, objections, and audience language.
- If the corpus is large and the task becomes research-heavy, hand off upstream to `review-mining-stp` or theory-analysis skills first.

## Default Analyze Output

Unless the user asks for another format, return:

1. content formula
2. hook patterns
3. pacing and structure pattern
4. tone and style notes
5. retention or share drivers
6. content gaps
7. reusable rules
