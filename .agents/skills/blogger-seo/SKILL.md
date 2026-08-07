---
name: blogger-seo
description: Optimize, audit, publish, or update Markdown articles in this repository for the AI 工具指南 Blogger site. Use for keyword planning, article SEO review, Blogger permalink and search-description setup, image optimization, structured-data checks, post-publication verification, or any request to improve rankings or organic search for posts under posts/drafts and posts/published.
---

# Blogger SEO

Apply this workflow only inside this repository. Treat Markdown plus YAML front matter as the canonical article source and use the existing `uv` CLI.

## Workflow

1. Read the target Markdown and `references/quality-gates.md`.
2. Preserve factual accuracy. Distinguish official product claims from independent testing and link primary sources.
3. Set one natural `primary_keyword`. Put it in the title, description, and opening 300 text characters without stuffing.
4. Use a concise lowercase English `slug`, 3 or more words, and 3–6 useful labels.
5. Keep the Blogger-generated page title as the only H1; begin article sections at H2.
6. Use `$blogger-images` for image generation or processing. Add descriptive alt text, explicit dimensions, at least one relevant internal link, and at least two primary-source links.
7. Run:

   ```bash
   UV_CACHE_DIR=.uv-cache uv run blogger validate <post.md>
   UV_CACHE_DIR=.uv-cache uv run blogger seo <post.md>
   UV_CACHE_DIR=.uv-cache uv run blogger preview <post.md>
   UV_CACHE_DIR=.uv-cache uv run blogger verify <published-post.md>
   UV_CACHE_DIR=.uv-cache uv run pytest -q
   ```

8. Do not publish unless `blogger seo` returns `score: 100` and tests pass. After publication, require `blogger verify` to return `score: 100`; source SEO alone is not a completed release gate.
9. For a new post, create a Blogger draft, set the custom permalink and per-post search description in Blogger, then publish through the CLI. Reuse `blogger_post_id`; never create a replacement post merely to update content.
10. After publishing, verify HTTP 200, canonical URL, title, meta description, indexability, external links, image rendering, desktop layout, and a 390 px mobile viewport. Confirm API status is `LIVE` and no template placeholders remain.

## Browser boundary

Prefer the Blogger API. Prefer stable GitHub Pages image URLs prepared by `$blogger-images`; use the browser only for Blogger settings the API cannot represent, especially custom permalinks, per-post search descriptions, theme changes, and legacy conversion of embedded images to Blogger-hosted HTTPS URLs. Preserve the existing URL when updating a published post.

## Definition of done

Report the public URL, source path, SEO score, tests, HTTP status, canonical result, mobile overflow result, and any platform limitation. Never promise a search ranking or indexing date; technical SEO can be verified, rankings cannot be guaranteed.
