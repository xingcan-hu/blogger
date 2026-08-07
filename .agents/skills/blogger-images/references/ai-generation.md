# AI-generated blog images

## Appropriate uses

- Article cover or hero illustration.
- Abstract explanation of an AI workflow.
- Decorative scene with useful negative space.
- Original concept art when no authentic product evidence is required.

## Prohibited substitutions

- Do not fabricate product screenshots, translated output, dashboards, quotas, test results, testimonials, logos, or comparisons.
- Do not imply an AI-generated person, office, document, or UI was observed during testing.
- Do not reproduce a living artist's style or create confusingly similar third-party branding.
- Do not include text inside the generated image unless necessary; rendered text is less accessible and harder to localize.

## Workflow

1. Use the installed `$imagegen` skill in built-in mode by default. Do not hard-code a model name; use the current supported default unless the user explicitly requests a CLI/API model path.
2. Generate a landscape cover at an aspect ratio appropriate for Blogger and social preview. Prefer a composition that remains legible when cropped.
3. Require no watermark, no fake interface, no unexplained logos, and no sensitive information.
4. Inspect the result for malformed objects, accidental text, branding, and misleading evidence.
5. Copy the selected project-bound output into `assets/source/<year>/<post-slug>/`.
6. Convert and publish it with `prepare_image.py`.
7. Use a factual alt description of what is visible, not the generation prompt.

## Prompt scaffold

```text
Use case: illustration-story or productivity-visual
Asset type: Chinese AI tools blog article cover
Primary request: <visual idea tied to the article>
Style/medium: clean editorial illustration
Composition/framing: landscape, clear focal point, safe crop area
Lighting/mood: trustworthy, practical, modern
Text: none
Constraints: no product UI, no logos, no watermark, no fabricated results
```
