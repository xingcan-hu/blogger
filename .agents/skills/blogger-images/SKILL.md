---
name: blogger-images
description: Prepare, optimize, name, publish, or verify images for Markdown articles in this AI 工具指南 Blogger repository. Use when Codex needs to process screenshots or illustrations, preserve small originals or optimize large files to WebP, generate SEO-safe filenames and alt text, build GitHub Pages image URLs, update image_dimensions front matter, or validate live Blogger images without relying on Blogger's browser uploader.
---

# Blogger Images

Apply this workflow only inside this repository. Keep original captures under `assets/source/` when they are worth retaining and publish optimized derivatives under `docs/images/<year>/<post-slug>/` for GitHub Pages.

## Prepare an image

1. Inspect the image for sensitive or irrelevant content. Crop browser chrome only when it does not remove evidence needed by the article.
2. Choose a lowercase ASCII filename describing the image, not `image-1` or `screenshot`.
3. Write concise Chinese alt text that describes the visible evidence in context. Do not stuff keywords or begin with “图片”。
4. Run the bundled script through the project environment:

   ```bash
   UV_CACHE_DIR=.uv-cache uv run python \
     .agents/skills/blogger-images/scripts/prepare_image.py \
     <source> \
     --output-dir docs/images/<year>/<post-slug> \
     --name <descriptive-name> \
     --alt '<contextual Chinese alt>' \
     --base-url https://xingcan-hu.github.io/blogger/images/<year>/<post-slug>
   ```

5. Copy the emitted Markdown image and `image_dimensions` values into the article front matter/body.
6. Run `$blogger-seo` checks before publishing.

## Generate an image when needed

Read `references/ai-generation.md` when an article needs a cover, concept illustration, visual metaphor, or other original raster artwork. Use the installed `$imagegen` skill and its built-in image generation path by default. Save the selected result into this workspace, then run `prepare_image.py` exactly as for any other source image.

Never generate or alter screenshots presented as product-test evidence. Use authentic captures for interfaces, benchmark results, prices, quotas, translated documents, and before/after comparisons. Label an AI-generated image in its caption when readers could reasonably mistake it for a real product screen or photograph.

## Publish through GitHub Pages

Read `references/github-pages.md` before enabling or changing Pages. Do not push unless the user authorized repository publication. Never place credentials, private documents, personal data, or confidential screenshots under `docs/`.

After the image commit is available on GitHub Pages, verify its HTTPS URL returns 200 and an image content type. Then publish or update Blogger through the API. Do not use `raw.githubusercontent.com` as the canonical image URL when Pages is available.

## Quality gates

- If the source image is 2 MB or smaller, preserve its original bytes, format, dimensions, and quality; do not resize, recompress, or convert it. Confirm it contains no EXIF metadata before publishing.
- Only optimize sources larger than 2 MB. Output WebP unless transparency, animation, or a platform constraint requires another format.
- For sources larger than 2 MB, prioritize legibility over aggressive compression. Default to a maximum width of 2560 px and WebP quality 92; preserve aspect ratio and never upscale.
- Strip EXIF metadata and normalize orientation when optimization is required. Reject an otherwise-preserved small source that contains EXIF until the metadata can be removed without lossy recompression.
- Keep each published image below 5 MB. Only reduce dimensions or quality when necessary to meet that limit, and visually confirm that interface text remains readable.
- Store explicit intrinsic width and height in `image_dimensions`.
- Use stable URLs; create a new filename when changing an already cached image materially.
- Preserve local source files until the published URL and Blogger page are verified.
- Record whether an asset is an authentic capture, supplied source, or AI-generated illustration.

## Definition of done

Report source and output paths, byte reduction, dimensions, Markdown, GitHub Pages URL, HTTP result if published, and the Blogger page that consumes it. A local conversion alone is not a published image.
