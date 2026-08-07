---
name: blogger-publish
description: Publish, republish, or update Markdown articles in this repository through the Blogger API with a CLI-first workflow. Use when Codex is asked to publish a new post, automatically publish completed work, update a live Blogger post, synchronize Blogger metadata back to posts/published, verify a release, or recover an interrupted Blogger publication without creating a duplicate post.
---

# Blogger Publish

Publish through the repository CLI and Blogger API. Treat browser automation as an exceptional fallback, never the default.

## Coordinate the repository skills

1. Use `$blogger-seo` to validate content and metadata before publishing.
2. Use `$blogger-images` when adding, processing, or verifying article images.
3. Use this skill for the external publication, metadata synchronization, recovery, and live verification stages.

When the user asks to add or create a blog post, publish it by default unless they explicitly request a draft or review-only output.

## Preflight

Work only with the canonical Markdown file under `posts/drafts/` or `posts/published/`. Preserve an existing `blogger_post_id` and URL.

Run:

```bash
UV_CACHE_DIR=.uv-cache uv run blogger validate <post.md>
UV_CACHE_DIR=.uv-cache uv run blogger seo <post.md>
UV_CACHE_DIR=.uv-cache uv run blogger preview <post.md>
UV_CACHE_DIR=.uv-cache uv run pytest -q
```

Publish only when validation passes, SEO is 100, tests pass, the slug is lowercase ASCII with at least three words, and no placeholders remain.

## Prefer the pure CLI path

Use the configured OAuth token and Blogger API. Do not open a browser merely to set a permalink or search description.

For a new post, use a slug-safe publish transaction implemented by the repository CLI:

1. Use the Markdown `slug` as a temporary English title.
2. Create the Blogger post as LIVE so Blogger locks a URL derived from that ASCII title.
3. Record the returned post ID immediately.
4. Patch the same live post with the final Chinese title, rendered HTML, and labels.
5. Confirm the final URL contains the intended slug and is not `blog-post.html` or `blog-post_<n>.html`.
6. Write `blogger_post_id`, `blogger_url`, `published_at`, `status: published`, and `updated_at` back to Markdown, then move it to `posts/published/`.

Keep the temporary-title interval as short as possible. If post creation succeeds but the final patch fails, retry the patch on the recorded post ID. Never insert a replacement post.

If the current CLI does not implement this transaction, stop before publishing and report the missing CLI capability. Offer to extend and test the publisher; do not silently switch to a browser or issue an unsafe sequence that could duplicate a post.

## Update an existing post

Require `blogger_post_id`. Patch that exact post through the API and preserve its public URL. Never create a new post to update content or repair metadata.

After updating, refresh `updated_at` and retain the original `published_at` unless Blogger reports a different authoritative value.

## Blogger API limitations

The official Blogger v3 Post resource has no supported writable `slug`, `permalink`, or per-post `searchDescription` field. Its deprecated `customMetaData` field is not a reliable substitute.

- Obtain a stable permalink through the temporary ASCII-title transaction above.
- Accept Blogger's generated page description when using a strictly browser-free workflow.
- Keep the desired description in Markdown even when Blogger cannot receive it through the API.
- Report the search-description limitation; do not claim that the exact text was applied.

Use a browser only when the user explicitly requests exact UI-only metadata or approves browser fallback after the limitation is explained.

## Failure recovery

- If an API call returns a post ID, save or retain it before retrying anything.
- If state is ambiguous, query that post ID with admin view and list LIVE/DRAFT posts before taking a write action.
- If the permalink is generic, do not delete or recreate the post automatically.
- If authentication needs first-time consent, ask the user to complete OAuth; reuse the token afterward.
- Treat permission, CAPTCHA, account selection, and protected workflows as stop conditions.

## Verify the live release

Confirm all of the following:

- Blogger API lists the expected post ID as LIVE.
- Public URL returns HTTP 200.
- Canonical equals the recorded public URL.
- Page title matches the final title.
- Meta description is present; distinguish generated text from an exact UI-set description.
- The page is not `noindex`.
- External links retain their HTTPS destinations.
- Images load, have useful alt text, and match recorded dimensions.
- Desktop and 390 px layouts have no horizontal overflow.
- No template placeholders remain.

Report the public URL, source path, post ID, SEO score, test result, HTTP and canonical results, mobile overflow result, and any Blogger platform limitation.
