---
name: clarify-and-minify
description: Relentlessly interview the user to resolve all ambiguities in a prompt, then output a minimal, token-efficient prompt for use with paid APIs. Use when user provides a prompt that needs clarification before being sent to another AI.
---

CRITICAL: You MUST conduct the interview in the SAME LANGUAGE as the user's original prompt. If the user writes in Chinese, you MUST speak Chinese and output the final minified prompt in Chinese. If the user writes in English, use English.

Interview me relentlessly about every ambiguous aspect of the provided prompt until we reach shared understanding.

For each question, provide your recommended answer. Present options as labeled choices (A, B, C...) when multiple reasonable answers exist. User can reply with the letter, say "recommended", or provide their own answer.

Ask one question at a time.

If a question can be answered by exploring the codebase, explore the codebase instead.

When the user's answer is itself ambiguous, continue追问 (with a recommended answer). If the same issue remains ambiguous after 3追问, adopt the most reasonable assumption and proceed.

If the user's answer contradicts a previously clarified decision, point out the conflict and let the user decide which prevails.

Prioritize questions in this order: core task objective and output format first, then details and edge cases.

Only after all ambiguities are resolved, output the final minified prompt in a pure text code block:

```text
[The final minified prompt only - no explanations, no extra text]