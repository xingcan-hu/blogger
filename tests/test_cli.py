from pathlib import Path

from blogger_publisher.cli import _generic_permalink, _live_seo_checks, _permalink_matches_slug, main
from blogger_publisher.content import load_article


ARTICLE = """---
title: PDFTranslator.org 体验
slug: pdftranslator-org-review
description: 这是一段用于测试命令行错误处理的中文摘要，详细介绍 PDF 翻译、排版保留、文件隐私、免费额度以及可复现的真实体验过程。
labels:
  - AI 工具
primary_keyword: PDF 翻译
status: draft
---

## 快速结论

正文。
"""


def article(tmp_path: Path) -> Path:
    path = tmp_path / "article.md"
    path.write_text(ARTICLE, encoding="utf-8")
    return path


def test_validate_command(tmp_path, capsys):
    assert main(["validate", str(article(tmp_path))]) == 0
    assert "VALID" in capsys.readouterr().out


def test_publish_requires_credentials(tmp_path, capsys):
    assert main(["publish", str(article(tmp_path))]) == 2
    assert "Provide --client-secret" in capsys.readouterr().err


def test_generic_permalink_detection():
    assert _generic_permalink("https://example.blogspot.com/2026/08/blog-post.html")
    assert _generic_permalink("https://example.blogspot.com/2026/08/blog-post_7.html")
    assert not _generic_permalink("https://example.blogspot.com/2026/08/pdftranslator-org-review.html")


def test_permalink_must_match_requested_slug():
    assert _permalink_matches_slug(
        "https://example.blogspot.com/2026/08/pdftranslator-org-review.html",
        "pdftranslator-org-review",
    )
    assert not _permalink_matches_slug(
        "https://example.blogspot.com/2026/08/another-review.html",
        "pdftranslator-org-review",
    )


def test_live_seo_checks_detect_url_mismatch(tmp_path):
    path = article(tmp_path)
    text = path.read_text(encoding="utf-8").replace(
        "status: draft", "status: published\nblogger_post_id: '123'\nblogger_url: https://example.blogspot.com/2026/08/pdftranslator-org-review.html"
    )
    path.write_text(text, encoding="utf-8")
    loaded = load_article(path)
    post = {
        "id": "123", "status": "LIVE", "url": "https://example.blogspot.com/2026/08/blog-post.html",
        "labels": ["AI 工具"],
    }
    html = "<html><head><title>PDFTranslator.org 体验</title><meta name='description' content='x'><link rel='canonical' href='https://example.blogspot.com/2026/08/blog-post.html'></head><body><article></article></body></html>"
    checks = {check.name: check for check in _live_seo_checks(loaded, post, html)}
    assert not checks["recorded_url"].passed
    assert not checks["slug_in_live_url"].passed
    assert not checks["canonical"].passed
