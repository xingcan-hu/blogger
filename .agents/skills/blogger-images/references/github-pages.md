# GitHub Pages image hosting for this project

## Layout

Publish from the repository `docs/` directory:

```text
docs/
└── images/
    └── 2026/
        └── pdftranslator-org-review/
            ├── upload-settings.webp
            └── bilingual-result.webp
```

The corresponding URL pattern is:

```text
https://xingcan-hu.github.io/blogger/images/<year>/<post-slug>/<filename>.webp
```

## Repository rules

- Require a public GitHub Pages URL before replacing a working Blogger-hosted image.
- Publish only optimized derivatives; retain large originals outside `docs/`.
- Prefer immutable descriptive filenames. Avoid query strings and branch-specific raw URLs.
- Do not use Git LFS objects as page image URLs.
- Do not assume Pages is enabled. Check repository settings or the expected URL first.
- Keep the existing Blogger-hosted URL when GitHub Pages is unavailable.

## Post-publish checks

- HTTP status 200.
- `Content-Type` starts with `image/`.
- URL uses HTTPS and remains stable without an authentication token.
- Natural dimensions match article `image_dimensions`.
- Blogger renders the image at desktop and 390 px viewport without horizontal overflow.
