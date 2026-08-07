# AI 工具指南 SEO quality gates

## Source gates

| Check | Project requirement |
| --- | --- |
| Title | 20–60 characters; specific benefit; natural primary keyword |
| Description | 70–160 characters; accurate summary; primary keyword |
| Slug | Lowercase ASCII, hyphenated, at least 3 words |
| Opening | Answer intent quickly; primary keyword within first 300 text characters |
| Structure | No body H1; at least 4 useful H2 sections |
| Depth | At least 1,500 rendered text characters; no padding or repetition |
| Labels | 3–6 stable taxonomy labels |
| Images | At least one relevant image; descriptive alt; `image_dimensions`; stable Blogger or GitHub Pages HTTPS URL; no sensitive information |
| Links | At least one useful internal link and two HTTPS primary-source links |
| Claims | Attribute product claims; record test date and method; disclose unverified limits |

The deterministic implementation lives in `src/blogger_publisher/content.py::seo_audit`. Update this table and that function together.

## Live-page gates

- HTTP status is 200.
- Canonical equals the intended public URL.
- Page title and meta description match the article.
- Page is not `noindex`.
- Images load with alt text and do not cause layout shift or horizontal overflow.
- External links retain their real HTTPS destinations.
- Blogger API returns `LIVE`, the expected labels, and the existing `blogger_post_id`.
- Default Blogger robots and `sitemap.xml` remain enabled unless a concrete indexing problem justifies a change.
- Article structured data has no critical validation errors. Do not manufacture ratings, reviews, author credentials, or dates.

Run `UV_CACHE_DIR=.uv-cache uv run blogger verify <published-post.md>` for every repository-managed live post. A source-only `blogger seo` score is never sufficient for a completed publication.

## Project URLs

- Blog: `https://aitooljournalhub.blogspot.com/`
- Sitemap: `https://aitooljournalhub.blogspot.com/sitemap.xml`
- Label hub pattern: `https://aitooljournalhub.blogspot.com/search/label/<URL-encoded-label>`

## Authoritative guidance

- Google Search Central: `https://developers.google.com/search/docs`
- Blogger SEO help: `https://support.google.com/blogger/answer/41373`
- Blogger settings help: `https://support.google.com/blogger/answer/9691230`

Re-check current official guidance before changing robots directives, structured data, or site-wide theme markup.
