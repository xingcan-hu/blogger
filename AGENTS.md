# Repository instructions

This repository manages the Markdown-first publishing workflow for the Chinese-language **AI 工具指南** Blogger site.

## Source of truth

- Treat Markdown under `posts/drafts/` and `posts/published/` as canonical. Do not make an unrecorded Blogger-only content edit.
- Keep reusable original images under `assets/source/` and public derivatives under `docs/images/<year>/<post-slug>/`.
- Preserve existing `blogger_post_id`, `blogger_url`, and publication timestamps. Updating an article must patch the recorded post, never insert a replacement.
- Never commit OAuth client secrets, `.blogger_token.json`, `.gsc_token.json`, private documents, or sensitive screenshots.

## Project skills

Use the smallest applicable set of skills in `.agents/skills/`:

- `$product-topic-brainstorm`: research a product URL and prioritize evidence-backed article ideas.
- `$blogger-natural-voice`: draft, rewrite, or localize natural-sounding article prose.
- `$blogger-seo`: plan keywords, audit metadata/content, and run pre/post-publication SEO gates.
- `$blogger-images`: prepare, optimize, publish, and verify article images.
- `$blogger-publish`: publish, update, recover, and verify Blogger releases through the repository CLI.

For a complete new article, normally apply topic research, natural voice, SEO, images, then publishing. Read each triggered skill completely and follow its cross-skill handoffs.

## Commands and checks

Use the project environment and repository-local cache:

```bash
UV_CACHE_DIR=.uv-cache uv sync
UV_CACHE_DIR=.uv-cache uv run blogger validate posts/drafts/article.md
UV_CACHE_DIR=.uv-cache uv run blogger seo posts/drafts/article.md
UV_CACHE_DIR=.uv-cache uv run blogger preview posts/drafts/article.md
UV_CACHE_DIR=.uv-cache uv run pytest -q
```

Before publishing, require validation success, SEO score 100, passing tests, no placeholders, and a lowercase ASCII slug of at least three words. After publishing or updating, run `blogger verify` and require score 100.

Use `blogger sitemap show|setup|submit|status` for Blogger's native sitemaps and Google Search Console. These commands interact with live Google services; do not run `setup` or `submit` unless the user requested or authorized that external change. OAuth may require the user to finish a browser consent or property-verification step.

## Editing conventions

- Start article body headings at H2 because Blogger renders the post title as H1.
- Preserve factual qualifications, primary-source links, Markdown structure, and Simplified Chinese locale unless the request changes them.
- Do not invent tests, first-hand experience, quotes, product claims, keyword volume, social engagement, rankings, or indexing dates.
- Prefer primary sources for product, policy, API, and other time-sensitive claims. Verify current facts on the web when needed.
- Keep unrelated user changes intact. The worktree may contain unpublished drafts and generated image assets.

## Live-operation boundaries

- Prefer the repository CLI and official APIs over browser automation.
- The Blogger API cannot set an exact per-post search description. Keep the desired description in Markdown and report the limitation instead of claiming it was applied.
- For new posts, rely on the CLI's temporary ASCII-title transaction to obtain the semantic permalink. If a write returns a post ID and a later step fails, recover that same post; do not create another one.
- Do not push, publish, update a live post, change Search Console state, or enable GitHub Pages without the user's authorization.
