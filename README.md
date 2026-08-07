# AI 工具指南 Blogger Publisher

Markdown-first publishing workflow for `https://aitooljournalhub.blogspot.com/`.

## Setup

```bash
UV_CACHE_DIR=.uv-cache uv sync
export BLOGGER_CLIENT_SECRET=/absolute/path/to/client_secret.json
```

OAuth tokens are stored in `.blogger_token.json`, set to mode `0600`, and ignored by Git.

## Commands

```bash
UV_CACHE_DIR=.uv-cache uv run blogger validate posts/drafts/article.md
UV_CACHE_DIR=.uv-cache uv run blogger seo posts/drafts/article.md
UV_CACHE_DIR=.uv-cache uv run blogger preview posts/drafts/article.md --open
UV_CACHE_DIR=.uv-cache uv run blogger draft posts/drafts/article.md
UV_CACHE_DIR=.uv-cache uv run blogger publish posts/drafts/article.md
UV_CACHE_DIR=.uv-cache uv run blogger update posts/published/article.md
UV_CACHE_DIR=.uv-cache uv run blogger verify posts/published/article.md
```

`draft` creates or updates a private Blogger draft. `publish` creates a draft when
needed, publishes it, and records the returned post ID and URL in the Markdown front
matter. Re-running either command updates the same post.

`seo` runs this project's deterministic pre-publish checks and exits non-zero unless
the article reaches 100. It checks the primary keyword, title and description lengths,
slug, headings, content depth, labels, image alt text, internal links, and source links.
`verify` is the required post-publish gate. It compares the canonical Markdown record
with Blogger's API and public HTML, including LIVE status, post ID, semantic permalink,
canonical URL, title, description, indexability, labels, and live image alt text.

## Content format

Each post uses YAML front matter with `title`, `slug`, `description`, `labels`, and
`status`. Start body headings at H2 because Blogger renders the post title as H1.
Local Markdown images are allowed when the file exists and has alt text; the renderer
embeds them in the generated HTML so drafts remain previewable without a separate
image host.

After a successful publish, the CLI writes `blogger_post_id`, `blogger_url`, and
`published_at`, then moves the source from `posts/drafts` to `posts/published`.

Project-only skills live in `.agents/skills/`. Use `$blogger-seo` for article SEO
and `$blogger-images` for authentic screenshots, optional AI-generated illustrations,
WebP conversion, image dimensions, and GitHub Pages image URLs.
