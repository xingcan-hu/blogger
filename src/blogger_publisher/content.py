"""Parse, validate, render, and update Markdown posts."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import base64
import mimetypes
from pathlib import Path
import re
from urllib.parse import urlparse

import bleach
from bs4 import BeautifulSoup
import frontmatter
from markdown_it import MarkdownIt
from mdit_py_plugins.tasklists import tasklists_plugin


REQUIRED_FIELDS = ("title", "slug", "description", "labels", "status", "primary_keyword")
ALLOWED_STATUS = {"draft", "published"}
ALLOWED_TAGS = set(bleach.sanitizer.ALLOWED_TAGS).union(
    {"article", "section", "h2", "h3", "h4", "h5", "h6", "p", "br", "hr",
     "pre", "code", "blockquote", "ul", "ol", "li", "table", "thead", "tbody",
     "tr", "th", "td", "figure", "figcaption", "img", "div", "span", "input"}
)
ALLOWED_ATTRIBUTES = {
    "a": ["href", "title", "rel", "target"],
    "img": ["src", "alt", "title", "width", "height", "loading"],
    "code": ["class"],
    "th": ["align"],
    "td": ["align"],
    "input": ["type", "checked", "disabled"],
    "div": ["class"],
    "span": ["class"],
}


class ContentError(ValueError):
    """Raised when a post cannot safely be published."""


@dataclass
class Article:
    path: Path
    metadata: dict
    body: str

    @property
    def title(self) -> str:
        return str(self.metadata["title"])


@dataclass(frozen=True)
class SeoCheck:
    name: str
    passed: bool
    detail: str


def load_article(path: Path) -> Article:
    if not path.exists():
        raise ContentError(f"Post not found: {path}")
    post = frontmatter.load(path)
    return Article(path=path, metadata=dict(post.metadata), body=post.content)


def validate_article(article: Article) -> list[str]:
    errors: list[str] = []
    meta = article.metadata
    for field in REQUIRED_FIELDS:
        if field not in meta or meta[field] in (None, "", []):
            errors.append(f"Missing required field: {field}")

    title = str(meta.get("title", ""))
    if len(title) > 60:
        errors.append("Title must be 60 characters or fewer")
    description = str(meta.get("description", ""))
    if not 50 <= len(description) <= 180:
        errors.append("Description must be between 50 and 180 characters")
    slug = str(meta.get("slug", ""))
    if slug and not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", slug):
        errors.append("Slug must use lowercase ASCII words separated by hyphens")
    status = str(meta.get("status", ""))
    if status and status not in ALLOWED_STATUS:
        errors.append("Status must be draft or published")

    labels = meta.get("labels", [])
    if not isinstance(labels, list) or not all(isinstance(label, str) for label in labels):
        errors.append("Labels must be a list of strings")
    elif len(labels) != len(set(labels)):
        errors.append("Labels must not contain duplicates")

    if re.search(r"^#\s+", article.body, flags=re.MULTILINE):
        errors.append("Body headings must start at H2; the Blogger title is the H1")

    rendered = _markdown().render(article.body)
    soup = BeautifulSoup(rendered, "html.parser")
    for image in soup.find_all("img"):
        if not image.get("alt", "").strip():
            errors.append(f"Image is missing alt text: {image.get('src', '<unknown>')}")
        source = image.get("src", "")
        if source and not _valid_image_source(article, source):
            errors.append(f"Invalid src URL or missing local image: {source}")
    for link in soup.find_all("a"):
        value = link.get("href", "")
        if value and not _valid_url(value):
            errors.append(f"Invalid href URL: {value}")
    if "{{" in article.body or "}}" in article.body:
        errors.append("Unresolved template placeholder found")
    return errors


def render_article(article: Article) -> str:
    errors = validate_article(article)
    if errors:
        raise ContentError("\n".join(errors))
    raw = _markdown().render(article.body)
    raw_soup = BeautifulSoup(raw, "html.parser")
    for image in raw_soup.find_all("img"):
        source = image.get("src", "")
        if source and not _valid_url(source):
            image["src"] = _image_data_url(article, source)
    clean = bleach.clean(
        str(raw_soup),
        tags=ALLOWED_TAGS,
        attributes=ALLOWED_ATTRIBUTES,
        protocols={"http", "https", "mailto", "data"},
        strip=True,
    )
    soup = BeautifulSoup(clean, "html.parser")
    for link in soup.find_all("a"):
        href = link.get("href", "")
        if href.startswith(("http://", "https://")):
            link["target"] = "_blank"
            link["rel"] = "noopener noreferrer"
    for image in soup.find_all("img"):
        image["loading"] = "lazy"
        dimensions = article.metadata.get("image_dimensions", {}).get(image.get("alt", ""))
        if isinstance(dimensions, list) and len(dimensions) == 2 and all(isinstance(value, int) and value > 0 for value in dimensions):
            image["width"], image["height"] = map(str, dimensions)
    return str(soup)


def seo_audit(article: Article) -> list[SeoCheck]:
    """Return deterministic source-level SEO checks for this Blogger project."""
    soup = BeautifulSoup(_markdown().render(article.body), "html.parser")
    text = soup.get_text(" ", strip=True)
    title = str(article.metadata.get("title", ""))
    description = str(article.metadata.get("description", ""))
    keyword = str(article.metadata.get("primary_keyword", "")).strip()
    labels = article.metadata.get("labels", [])
    slug = str(article.metadata.get("slug", ""))
    links = [link.get("href", "") for link in soup.find_all("a")]
    images = soup.find_all("img")
    dimensions = article.metadata.get("image_dimensions", {})
    internal = [url for url in links if "aitooljournalhub.blogspot.com" in url]
    sources = [url for url in links if url.startswith("https://") and "aitooljournalhub.blogspot.com" not in url]
    checks = [
        SeoCheck("title_length", 20 <= len(title) <= 60, f"{len(title)} characters (target 20-60)"),
        SeoCheck("description_length", 70 <= len(description) <= 160, f"{len(description)} characters (target 70-160)"),
        SeoCheck("keyword_in_title", bool(keyword and keyword.lower() in title.lower()), keyword or "missing keyword"),
        SeoCheck("keyword_in_description", bool(keyword and keyword.lower() in description.lower()), keyword or "missing keyword"),
        SeoCheck("keyword_in_intro", bool(keyword and keyword.lower() in text[:300].lower()), keyword or "missing keyword"),
        SeoCheck("readable_slug", len(slug.split("-")) >= 3, slug),
        SeoCheck("heading_structure", not soup.find("h1") and len(soup.find_all("h2")) >= 4, f"{len(soup.find_all('h2'))} H2 headings"),
        SeoCheck("substantial_content", len(text) >= 1500, f"{len(text)} text characters"),
        SeoCheck("labels", isinstance(labels, list) and 3 <= len(labels) <= 6, f"{len(labels) if isinstance(labels, list) else 0} labels"),
        SeoCheck("descriptive_images", bool(images) and all(img.get("alt", "").strip() for img in images), f"{len(images)} images"),
        SeoCheck("image_dimensions", bool(images) and all(
            isinstance(dimensions.get(img.get("alt", "")), list)
            and len(dimensions[img.get("alt", "")]) == 2
            and all(isinstance(value, int) and value > 0 for value in dimensions[img.get("alt", "")])
            for img in images
        ), f"{len(dimensions) if isinstance(dimensions, dict) else 0} dimension records"),
        SeoCheck("internal_links", len(internal) >= 1, f"{len(internal)} internal links"),
        SeoCheck("source_links", len(sources) >= 2, f"{len(sources)} external source links"),
    ]
    return checks


def save_metadata(article: Article, **updates: object) -> Path:
    article.metadata.update({key: value for key, value in updates.items() if value is not None})
    post = frontmatter.Post(article.body, **article.metadata)
    article.path.write_text(frontmatter.dumps(post) + "\n", encoding="utf-8")
    return article.path


def mark_published(article: Article, post_id: str, url: str, published_at: str | None = None) -> Path:
    timestamp = published_at or datetime.now(timezone.utc).isoformat()
    save_metadata(
        article,
        status="published",
        blogger_post_id=str(post_id),
        blogger_url=url,
        published_at=timestamp,
        updated_at=datetime.now(timezone.utc).date().isoformat(),
    )
    if article.path.parent.name == "drafts":
        destination = article.path.parent.parent / "published" / article.path.name
        destination.parent.mkdir(parents=True, exist_ok=True)
        article.path.replace(destination)
        article.path = destination
    return article.path


def _markdown() -> MarkdownIt:
    return MarkdownIt("commonmark", {"html": False, "linkify": True, "typographer": True}).enable("table").use(tasklists_plugin)


def _valid_url(value: str) -> bool:
    if value.startswith("#"):
        return True
    parsed = urlparse(value)
    return parsed.scheme in {"http", "https", "mailto"} and bool(parsed.netloc or parsed.scheme == "mailto")


def _local_image_path(article: Article, value: str) -> Path:
    return (article.path.parent / value).resolve()


def _valid_image_source(article: Article, value: str) -> bool:
    if _valid_url(value):
        return True
    path = _local_image_path(article, value)
    return path.is_file() and path.suffix.lower() in {".png", ".jpg", ".jpeg", ".webp", ".gif"}


def _image_data_url(article: Article, value: str) -> str:
    path = _local_image_path(article, value)
    mime_type = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
    encoded = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:{mime_type};base64,{encoded}"
