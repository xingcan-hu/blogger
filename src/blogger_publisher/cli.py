"""Command-line interface for the Blogger Markdown workflow."""

from __future__ import annotations

import argparse
from html import escape
import json
import os
from pathlib import Path
import sys
from urllib.parse import urlparse
from urllib.request import Request, urlopen
from xml.etree import ElementTree
import webbrowser

from bs4 import BeautifulSoup

from .api import BloggerClient, BloggerError, SearchConsoleClient
from .content import ContentError, load_article, mark_published, render_article, save_metadata, seo_audit, validate_article


PROJECT_ROOT = Path.cwd()
DEFAULT_TOKEN = PROJECT_ROOT / ".blogger_token.json"
DEFAULT_GSC_TOKEN = PROJECT_ROOT / ".gsc_token.json"


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(prog="blogger", description="Publish Markdown posts to Blogger")
    root.add_argument("--client-secret", type=Path, default=os.getenv("BLOGGER_CLIENT_SECRET"))
    root.add_argument("--token", type=Path, default=DEFAULT_TOKEN)
    root.add_argument("--gsc-token", type=Path, default=DEFAULT_GSC_TOKEN)
    root.add_argument("--gsc-site", default=os.getenv("GSC_SITE_URL"))
    commands = root.add_subparsers(dest="command", required=True)
    for name in ("validate", "seo", "preview", "verify", "draft", "publish", "update"):
        command = commands.add_parser(name)
        command.add_argument("post", type=Path)
    commands.choices["preview"].add_argument("--open", action="store_true", dest="open_browser")
    sitemap = commands.add_parser("sitemap", help="Submit Blogger's generated sitemaps to GSC")
    sitemap.add_argument("action", choices=("show", "setup", "submit", "status"))
    return root


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    try:
        if args.command == "sitemap":
            return _sitemap_command(args)
        article = load_article(args.post)
        if args.command == "validate":
            errors = validate_article(article)
            if errors:
                raise ContentError("\n".join(errors))
            print(f"VALID {article.path}")
            return 0
        if args.command == "seo":
            errors = validate_article(article)
            if errors:
                raise ContentError("\n".join(errors))
            checks = seo_audit(article)
            print(json.dumps({
                "score": round(100 * sum(check.passed for check in checks) / len(checks)),
                "checks": [check.__dict__ for check in checks],
            }, ensure_ascii=False, indent=2))
            return 0 if all(check.passed for check in checks) else 2
        html = render_article(article)
        if args.command == "preview":
            output = _preview(article.title, article.metadata["description"], html)
            if args.open_browser:
                webbrowser.open(output.as_uri())
            print(output)
            return 0
        if not args.client_secret and not args.token.is_file():
            raise BloggerError("Provide --client-secret/BLOGGER_CLIENT_SECRET or an existing --token file")
        client = BloggerClient(Path(args.client_secret) if args.client_secret else None, args.token)
        post_id = article.metadata.get("blogger_post_id")
        if args.command == "verify":
            if not post_id:
                raise BloggerError("Cannot verify a post without blogger_post_id")
            post = client.get(str(post_id))
            checks = _live_seo_checks(article, post, _fetch_html(str(post.get("url", ""))))
            print(json.dumps({
                "score": round(100 * sum(check.passed for check in checks) / len(checks)),
                "checks": [check.__dict__ for check in checks],
            }, ensure_ascii=False, indent=2))
            return 0 if all(check.passed for check in checks) else 2
        labels = list(article.metadata["labels"])
        if args.command == "publish":
            slug = str(article.metadata["slug"])
            if post_id:
                post = client.get(str(post_id))
                if post.get("status") != "LIVE":
                    client.patch(str(post_id), slug, html, labels)
                    post = client.publish(str(post_id))
                    save_metadata(article, blogger_post_id=str(post_id), blogger_url=post.get("url"))
                    if not _permalink_matches_slug(str(post.get("url", "")), slug):
                        raise BloggerError(
                            f"Recovered post {post_id}, but its permalink does not match the requested slug: "
                            f"{post.get('url', '')}"
                        )
                post = client.patch(str(post_id), article.title, html, labels)
            else:
                post = client.create_live(slug, html, labels)
                post_id = str(post["id"])
                save_metadata(article, blogger_post_id=post_id, blogger_url=post.get("url"))
                if not _permalink_matches_slug(str(post.get("url", "")), slug):
                    raise BloggerError(
                        f"Post {post_id} is live, but its permalink does not match the requested slug; "
                        f"repair this post instead of creating another: {post.get('url', '')}"
                    )
                post = client.patch(post_id, article.title, html, labels)
        elif post_id:
            post = client.patch(str(post_id), article.title, html, labels)
        elif args.command == "update":
            raise BloggerError("Cannot update a post without blogger_post_id")
        else:
            post = client.create_draft(article.title, html, labels)
            post_id = str(post["id"])
            save_metadata(article, blogger_post_id=post_id, blogger_url=post.get("url"))
        if args.command == "publish":
            live_url = post.get("url", "")
            if not _permalink_matches_slug(live_url, str(article.metadata["slug"])):
                raise BloggerError(
                    f"Published post permalink does not match the requested slug: {live_url}"
                )
            final_path = mark_published(
                article,
                str(post["id"]),
                post["url"],
                post.get("published"),
            )
        else:
            final_path = article.path
        result = {
            "blog": client.blog["name"],
            "post_id": str(post["id"]),
            "title": post["title"],
            "status": post.get("status"),
            "url": post.get("url"),
            "source": str(final_path),
        }
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    except (ContentError, BloggerError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 2


def _sitemap_command(args) -> int:
    if not args.client_secret and not args.token.is_file():
        raise BloggerError("Provide --client-secret/BLOGGER_CLIENT_SECRET or an existing --token file")
    client_secret = Path(args.client_secret) if args.client_secret else None
    blogger = BloggerClient(client_secret, args.token)
    blog_url = str(blogger.blog.get("url", "")).rstrip("/")
    if not blog_url.startswith("https://"):
        raise BloggerError(f"Expected an HTTPS Blogger URL, got: {blog_url or '<missing>'}")
    sitemap_urls = [f"{blog_url}/sitemap.xml", f"{blog_url}/sitemap-pages.xml"]
    if args.action == "show":
        print(json.dumps({"blog": blog_url, "sitemaps": sitemap_urls}, indent=2))
        return 0
    if not args.client_secret and not args.gsc_token.is_file() and not args.token.is_file():
        raise BloggerError(
            "GSC OAuth token is missing; provide --client-secret/BLOGGER_CLIENT_SECRET for first authorization"
        )
    gsc = SearchConsoleClient(client_secret, args.gsc_token, oauth_source=args.token)
    if args.action == "setup":
        site_url = blog_url + "/"
        gsc.add_site(site_url)
        result = gsc.site(site_url)
        print(json.dumps({"site": site_url, **result}, ensure_ascii=False, indent=2))
        if result.get("permissionLevel") == "siteUnverifiedUser":
            raise BloggerError(
                "GSC property was added but is not verified; verify ownership in Search Console, then run sitemap submit"
            )
        return 0
    site_url = gsc.resolve_site(blog_url, args.gsc_site)
    if args.action == "status":
        submitted = {
            str(item.get("path")): item for item in gsc.list_sitemaps(site_url)
        }
        results = [submitted[url] for url in sitemap_urls if url in submitted]
        print(json.dumps({"site": site_url, "sitemaps": results}, ensure_ascii=False, indent=2))
        return 0
    results = []
    for sitemap_url in sitemap_urls:
        if _sitemap_has_entries(sitemap_url):
            gsc.submit(site_url, sitemap_url)
            results.append({"path": sitemap_url, "submitted": True})
        else:
            try:
                gsc.delete(site_url, sitemap_url)
            except Exception as error:
                if getattr(getattr(error, "resp", None), "status", None) != 404:
                    raise
            results.append({"path": sitemap_url, "submitted": False, "reason": "empty sitemap"})
    print(json.dumps({"site": site_url, "sitemaps": results}, ensure_ascii=False, indent=2))
    return 0


def _sitemap_has_entries(url: str) -> bool:
    try:
        with urlopen(Request(url, headers={"User-Agent": "blogger-publisher-sitemap/1.0"}), timeout=30) as response:
            root = ElementTree.fromstring(response.read())
    except (OSError, ElementTree.ParseError) as error:
        raise BloggerError(f"Could not read sitemap {url}: {error}") from error
    return any(child.tag.rsplit("}", 1)[-1] in {"url", "sitemap"} for child in root)


def _preview(title: str, description: str, content: str) -> Path:
    output = PROJECT_ROOT / ".preview" / "post.html"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        "<!doctype html><html lang='zh-CN'><head><meta charset='utf-8'>"
        f"<meta name='description' content='{escape(str(description), quote=True)}'>"
        "<meta name='viewport' content='width=device-width,initial-scale=1'>"
        f"<title>{escape(title)}</title><style>body{{font:18px/1.75 system-ui;max-width:800px;margin:40px auto;padding:0 20px}}img{{max-width:100%}}table{{border-collapse:collapse;width:100%}}td,th{{border:1px solid #bbb;padding:8px}}code{{overflow-wrap:anywhere}}</style>"
        f"</head><body><article><h1>{escape(title)}</h1>{content}</article></body></html>",
        encoding="utf-8",
    )
    return output.resolve()


def _generic_permalink(url: str) -> bool:
    name = Path(urlparse(url).path).name
    return name == "blog-post.html" or name.startswith("blog-post_")


def _permalink_matches_slug(url: str, slug: str) -> bool:
    return Path(urlparse(url).path).stem == slug and not _generic_permalink(url)


def _fetch_html(url: str) -> str:
    if not url.startswith("https://"):
        raise BloggerError(f"Expected an HTTPS public URL, got: {url or '<missing>'}")
    try:
        with urlopen(Request(url, headers={"User-Agent": "blogger-publisher-seo-verifier/1.0"}), timeout=30) as response:
            if response.status != 200:
                raise BloggerError(f"Public URL returned HTTP {response.status}: {url}")
            return response.read().decode("utf-8", errors="replace")
    except OSError as error:
        raise BloggerError(f"Could not fetch public URL {url}: {error}") from error


def _live_seo_checks(article, post: dict, html: str):
    soup = BeautifulSoup(html, "html.parser")
    expected_url = str(article.metadata.get("blogger_url", ""))
    actual_url = str(post.get("url", ""))
    canonical = soup.find("link", rel="canonical")
    description = soup.find("meta", attrs={"name": "description"})
    robots = soup.find("meta", attrs={"name": "robots"})
    title = soup.find("title")
    images = soup.select("article img")
    from .content import SeoCheck
    return [
        SeoCheck("api_live", post.get("status") == "LIVE", str(post.get("status"))),
        SeoCheck("post_id", str(post.get("id")) == str(article.metadata.get("blogger_post_id")), str(post.get("id"))),
        SeoCheck("recorded_url", bool(expected_url and actual_url == expected_url), actual_url),
        SeoCheck("slug_in_live_url", _permalink_matches_slug(actual_url, str(article.metadata.get("slug", ""))), actual_url),
        SeoCheck("canonical", bool(canonical and canonical.get("href") == expected_url), canonical.get("href", "") if canonical else "missing"),
        SeoCheck("live_title", bool(title and title.get_text(strip=True) == article.title), title.get_text(strip=True) if title else "missing"),
        SeoCheck("live_description", bool(description and description.get("content") == str(article.metadata.get("description", ""))), description.get("content", "") if description else "missing"),
        SeoCheck("indexable", not robots or "noindex" not in robots.get("content", "").lower(), robots.get("content", "") if robots else "no robots restriction"),
        SeoCheck("live_labels", sorted(post.get("labels", [])) == sorted(article.metadata.get("labels", [])), ", ".join(post.get("labels", []))),
        SeoCheck("live_image_alt", all(image.get("alt", "").strip() for image in images), f"{len(images)} article images"),
    ]


if __name__ == "__main__":
    raise SystemExit(main())
