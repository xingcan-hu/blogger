---
name: blogger-seo
description: Optimize, audit, or verify Markdown articles and search visibility in this repository for the AI 工具指南 Blogger site. Use for keyword planning, article SEO review, Blogger permalink and search-description constraints, image optimization, structured-data checks, sitemap and Google Search Console checks, post-publication verification, or requests to improve organic search for posts under posts/drafts and posts/published.
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
9. For a new post, hand off to `$blogger-publish`. Let the CLI use its temporary ASCII-title transaction to obtain a semantic permalink, then patch the same post with the final title and content. Reuse `blogger_post_id`; never create a replacement post merely to update content.
10. After publishing, verify HTTP 200, canonical URL, title, meta description, indexability, external links, image rendering, desktop layout, and a 390 px mobile viewport. Confirm API status is `LIVE` and no template placeholders remain.

## Search Console and sitemaps

Use Blogger's native sitemap URLs; do not generate or upload a local XML sitemap:

```bash
UV_CACHE_DIR=.uv-cache uv run blogger sitemap show
UV_CACHE_DIR=.uv-cache uv run blogger sitemap setup
UV_CACHE_DIR=.uv-cache uv run blogger sitemap submit
UV_CACHE_DIR=.uv-cache uv run blogger sitemap status
```

- Use `show` to inspect URLs without changing Search Console.
- Run `setup` or `submit` only when the user authorized the external change. `setup` may still require ownership verification in Search Console.
- `submit` selects a matching verified property, submits non-empty native sitemaps, and removes stale empty submissions. Use `--gsc-site` or `GSC_SITE_URL` when an explicit property is required.
- Use `status` to report submission/download timestamps, errors, and warnings. Do not describe submission as proof of indexing.

## Browser boundary

Prefer the Blogger and Search Console APIs. Prefer stable GitHub Pages image URLs prepared by `$blogger-images`. The Blogger API cannot set an exact per-post search description; retain the desired description in Markdown and report that limitation. Use a browser only when the user explicitly requests an exact UI-only change or approves that fallback. Preserve the existing URL when updating a published post.

## Definition of done

Report the public URL, source path, SEO score, tests, HTTP status, canonical result, mobile overflow result, and any platform limitation. Never promise a search ranking or indexing date; technical SEO can be verified, rankings cannot be guaranteed.
