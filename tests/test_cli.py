from pathlib import Path

from blogger_publisher.cli import _generic_permalink, _live_seo_checks, _permalink_matches_slug, main
from blogger_publisher.content import load_article
import blogger_publisher.cli as cli


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
    assert main(["--token", str(tmp_path / "missing-token.json"), "publish", str(article(tmp_path))]) == 2
    assert "existing --token" in capsys.readouterr().err


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


def test_publish_uses_slug_then_restores_title(tmp_path, monkeypatch):
    calls = []

    class FakeClient:
        blog = {"name": "Test Blog"}

        def __init__(self, client_secret, token):
            pass

        def create_draft(self, title, content, labels):
            calls.append(("create_draft", title))
            return {"id": "123", "title": title, "status": "DRAFT", "url": ""}

        def publish(self, post_id):
            calls.append(("publish", post_id))
            return {
                "id": post_id,
                "title": "pdftranslator-org-review",
                "status": "LIVE",
                "url": "https://example.blogspot.com/2026/08/pdftranslator-org-review.html",
                "published": "2026-08-07T00:00:00Z",
            }

        def patch(self, post_id, title, content, labels):
            calls.append(("patch", title))
            return {
                "id": post_id,
                "title": title,
                "status": "LIVE",
                "url": "https://example.blogspot.com/2026/08/pdftranslator-org-review.html",
                "published": "2026-08-07T00:00:00Z",
            }

    monkeypatch.setattr(cli, "BloggerClient", FakeClient)
    token = tmp_path / "token.json"
    token.write_text("{}", encoding="utf-8")
    drafts = tmp_path / "drafts"
    drafts.mkdir()
    source = article(drafts)

    assert main(["--token", str(token), "publish", str(source)]) == 0
    assert calls == [
        ("create_draft", "pdftranslator-org-review"),
        ("publish", "123"),
        ("patch", "PDFTranslator.org 体验"),
    ]
    published = tmp_path / "published" / source.name
    assert published.is_file()
    loaded = load_article(published)
    assert loaded.metadata["blogger_post_id"] == "123"
    assert loaded.metadata["status"] == "published"
