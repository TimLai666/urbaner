# Mode selection and language rules

Use this routing logic before drafting.

## 1. Rewrite vs generate

- Choose `rewrite` when the user provides source text, a draft, or a paragraph to fix.
- Choose `generate` when the user wants new prose from intent, bullets, notes, or context.
- If the request includes both notes and a rough draft, prefer `rewrite` and keep what already works.

## 2. Grounded vs voiced

Choose `grounded` when the text is:

- professional
- factual
- internal
- operational
- explanatory
- trust-sensitive

Choose `voiced` when the text is:

- persuasive
- editorial
- opinionated
- social
- brand-led
- meant to sound personal or distinctive

If the prompt is ambiguous:

- default to `grounded` for business, documentation, updates, or neutral explanation
- default to `voiced` for essays, commentary, posts, and marketing-style asks

## 3. Language handling

- Match the user's language by default.
- Preserve the source language in rewrite mode unless asked to translate.
- Preserve deliberate code-switching in bilingual input.
- Do not force English sentence logic onto Chinese prose.
- Do not force Chinese rhetorical density onto English prose.

## 4. Output defaults

- Keep meaning stable in `rewrite`.
- Keep invention low when details are missing in `generate`.
- Prefer one strong draft over multiple padded options unless the user asks for variants.
