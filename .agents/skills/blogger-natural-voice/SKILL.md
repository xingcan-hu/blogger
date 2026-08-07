---
name: blogger-natural-voice
description: Draft, rewrite, or review blog articles so they sound naturally written by a local human rather than generated or mechanically translated. Use for posts under posts/drafts and posts/published, or whenever a user asks to remove AI flavor, reduce formulaic prose, improve blog voice, add appropriate written polish, or localize wording for a target language, country, or region while preserving facts and meaning.
---

# Blogger Natural Voice

Write with a recognizable human point of view, natural rhythm, and locally appropriate phrasing. Keep the prose polished enough for a published article without making it stiff, promotional, or artificially conversational.

## Establish context

1. Read the entire article before editing. Identify its audience, purpose, author stance, and technical depth.
2. Determine the target locale from the user's request, front matter, site context, and source text. Ask only when choosing the wrong locale would materially change the result; otherwise preserve the source locale.
3. Preserve facts, qualifications, links, product names, quoted material, Markdown structure, and SEO fields unless the user asks to change them. Never invent personal experience, test results, emotions, sources, or local idioms.
4. Apply `$blogger-seo` as well when the request includes keyword planning, ranking, metadata, publishing, or SEO validation. Let factual accuracy and natural reading take priority over exact-match keyword repetition.

## Draft or rewrite

1. Lead with the reader's actual question, situation, observation, or decision. Avoid a generic scene-setting paragraph that could introduce any article.
2. Give each paragraph one useful job. Connect ideas through meaning instead of repeatedly using stock transitions.
3. Vary sentence length and structure according to the content. Use short sentences for emphasis sparingly; use longer sentences when a relationship needs explanation.
4. Prefer concrete nouns, active verbs, specific examples, and verifiable details. Replace abstract praise and inflated claims with evidence or a precise limitation.
5. Keep an identifiable stance. State what matters, what is uncertain, and where the tradeoff lies instead of presenting every point with symmetrical, impersonal neutrality.
6. Use headings and lists only when they improve scanning. Do not force every section into the same length, cadence, or number of bullets.
7. End when the article has delivered its answer. Do not append a generic recap, inspirational slogan, or invitation to “explore the future” unless it serves the reader.

## Remove mechanical patterns

Revise patterns such as these when they appear without a real communicative purpose:

- Repeated templates such as “不只是……更是……”, “无论你是……还是……”, or “在当今快速发展的时代”.
- Consecutive paragraphs with identical openings, lengths, or conclusion sentences.
- Excessive signposting such as “首先、其次、此外、最后、综上所述” when the logic is already clear.
- Empty authority signals, grand claims, vague intensifiers, and promotional adjectives unsupported by evidence.
- Over-explaining obvious points, restating a heading in the first sentence, or repeating the same conclusion in several forms.
- Fake intimacy, rhetorical questions in every section, staged hesitations, excessive asides, deliberate typos, or forced slang added merely to appear human.

Treat these as diagnostic signals, not a word blacklist. Keep any phrase that is accurate, idiomatic, and useful in context.

## Localize the language

1. Follow the target locale's vocabulary, spelling, punctuation, units, date formats, address conventions, and level of directness.
2. Write for local readers rather than translating source syntax. Rebuild sentences whose word order or collocations feel imported from another language.
3. Prefer expressions that are broadly natural in the target locale. Use regional slang, internet language, and culture-specific analogies only when the audience and publication voice support them.
4. For Simplified Chinese aimed at mainland readers, prefer concise subject omission where clear, full-width Chinese punctuation, familiar local terminology, and measured written phrasing. Avoid literal English connective chains and unnecessary pronouns.
5. Preserve established product terminology when it helps recognition. Explain an unfamiliar localized term once instead of switching labels throughout the article.

## Final pass

Read the revision as continuous prose and confirm:

- The opening is specific to this article.
- The authorial stance sounds credible without inventing experience.
- Sentence rhythm and paragraph shapes vary naturally.
- Claims remain factual and appropriately qualified.
- The vocabulary and conventions fit the target locale.
- Removing any remaining sentence would not eliminate repetition or filler.
- The article is polished but does not sound like an advertisement, a report template, or a line-by-line translation.

Report any factual ambiguity, missing locale context, or original claim that could not be safely preserved. Do not claim that a detector score proves human authorship; judge the result by clarity, specificity, consistency, and local naturalness.
