from pathlib import Path

import pytest

from blogger_publisher.content import ContentError, load_article, mark_published, render_article, save_metadata, seo_audit, validate_article


GOOD = """---
title: PDFTranslator.org 体验
slug: pdftranslator-org-review
description: 这是一段用于测试文章元数据校验的中文摘要，详细介绍 PDF 文档翻译、原始排版保留、文件隐私规则、免费使用额度以及一次可复现的真实使用体验。
labels:
  - AI 工具
primary_keyword: PDF 翻译
status: draft
---

## 快速结论

[官网](https://example.com)提供翻译功能。
"""


def write(tmp_path: Path, text: str = GOOD) -> Path:
    path = tmp_path / "post.md"
    path.write_text(text, encoding="utf-8")
    return path


def test_parse_and_render(tmp_path):
    article = load_article(write(tmp_path))
    assert validate_article(article) == []
    html = render_article(article)
    assert "<h2>快速结论</h2>" in html
    assert 'rel="noopener noreferrer"' in html


@pytest.mark.parametrize(
    "replacement,expected",
    [
        ("title: PDFTranslator.org 体验\n", "Missing required field: title"),
        ("  - AI 工具\nprimary_keyword", "Labels must not contain duplicates"),
        ("## 快速结论", "Image is missing alt text"),
        ("https://example.com", "Invalid href URL"),
    ],
)
def test_validation_failures(tmp_path, replacement, expected):
    if expected.startswith("Missing"):
        text = GOOD.replace(replacement, "")
    elif expected.startswith("Labels"):
        text = GOOD.replace(replacement, "  - AI 工具\n  - AI 工具\nprimary_keyword")
    elif expected.startswith("Image"):
        text = GOOD.replace(replacement, "## 快速结论\n\n![](https://example.com/a.png)")
    else:
        text = GOOD.replace(replacement, "https:///broken")
    errors = validate_article(load_article(write(tmp_path, text)))
    assert expected in "\n".join(errors)


def test_html_is_sanitized(tmp_path):
    article = load_article(write(tmp_path, GOOD + "\n<script>alert(1)</script>"))
    html = render_article(article)
    assert "<script" not in html


def test_render_embeds_existing_local_image(tmp_path):
    image = tmp_path / "shot.png"
    image.write_bytes(b"\x89PNG\r\n\x1a\n")
    article = load_article(write(tmp_path, GOOD + "\n![screen](shot.png)"))

    html = render_article(article)

    assert 'src="data:image/png;base64,' in html
    assert 'alt="screen"' in html


def test_missing_local_image_fails_validation(tmp_path):
    article = load_article(write(tmp_path, GOOD + "\n![screen](missing.png)"))

    errors = validate_article(article)

    assert any("missing local image" in error for error in errors)


def test_metadata_writeback_and_move(tmp_path):
    drafts = tmp_path / "posts" / "drafts"
    drafts.mkdir(parents=True)
    article = load_article(write(drafts))
    save_metadata(article, blogger_post_id="123")
    assert load_article(article.path).metadata["blogger_post_id"] == "123"
    destination = mark_published(article, "123", "https://example.com/post")
    assert destination.parent.name == "published"
    saved = load_article(destination)
    assert saved.metadata["status"] == "published"
    assert saved.metadata["blogger_url"] == "https://example.com/post"


def test_published_article_passes_project_seo_audit():
    path = Path(__file__).parents[1] / "posts" / "published" / "pdftranslator-org.md"
    checks = seo_audit(load_article(path))

    assert all(check.passed for check in checks), [check for check in checks if not check.passed]
