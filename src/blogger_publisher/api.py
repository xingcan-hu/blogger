"""Google OAuth and Blogger API operations."""

from __future__ import annotations

import json
from pathlib import Path
from urllib.parse import urlparse

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build


BLOGGER_SCOPES = ["https://www.googleapis.com/auth/blogger"]
GSC_SCOPES = ["https://www.googleapis.com/auth/webmasters"]


class BloggerError(RuntimeError):
    """Raised when Blogger state is ambiguous or unsafe."""


class BloggerClient:
    def __init__(self, client_secret: Path | None, token_path: Path):
        self.token_path = token_path
        self.service = build(
            "blogger", "v3", credentials=_credentials(client_secret, token_path, BLOGGER_SCOPES)
        )
        self.blog = self._single_blog()

    def _single_blog(self) -> dict:
        blogs = self.service.blogs().listByUser(userId="self").execute().get("items", [])
        if len(blogs) != 1:
            raise BloggerError(f"Expected exactly one Blogger blog, found {len(blogs)}")
        return blogs[0]

    def create_draft(self, title: str, content: str, labels: list[str]) -> dict:
        return self.service.posts().insert(
            blogId=self.blog["id"],
            isDraft=True,
            body={"title": title, "content": content, "labels": labels},
        ).execute()

    def create_live(self, title: str, content: str, labels: list[str]) -> dict:
        return self.service.posts().insert(
            blogId=self.blog["id"],
            isDraft=False,
            body={"title": title, "content": content, "labels": labels},
        ).execute()

    def patch(self, post_id: str, title: str, content: str, labels: list[str]) -> dict:
        return self.service.posts().patch(
            blogId=self.blog["id"],
            postId=post_id,
            body={"title": title, "content": content, "labels": labels},
        ).execute()

    def publish(self, post_id: str) -> dict:
        return self.service.posts().publish(blogId=self.blog["id"], postId=post_id).execute()

    def get(self, post_id: str) -> dict:
        return self.service.posts().get(blogId=self.blog["id"], postId=post_id, view="ADMIN").execute()


class SearchConsoleClient:
    """Submit and inspect Blogger's native sitemaps in Search Console."""

    def __init__(
        self, client_secret: Path | None, token_path: Path, oauth_source: Path | None = None
    ):
        credentials = _credentials(client_secret, token_path, GSC_SCOPES, oauth_source)
        self.service = build("searchconsole", "v1", credentials=credentials)

    def resolve_site(self, blog_url: str, requested_site: str | None = None) -> str:
        entries = self.service.sites().list().execute().get("siteEntry", [])
        verified = [
            entry for entry in entries
            if entry.get("permissionLevel") != "siteUnverifiedUser"
        ]
        if requested_site:
            if any(entry.get("siteUrl") == requested_site for entry in verified):
                return requested_site
            raise BloggerError(
                f"GSC property is not verified or accessible: {requested_site}"
            )

        blog_url = blog_url.rstrip("/") + "/"
        host = (urlparse(blog_url).hostname or "").lower()

        def score(entry: dict) -> tuple[int, int]:
            site = str(entry.get("siteUrl", ""))
            if site.startswith("sc-domain:"):
                domain = site.removeprefix("sc-domain:").lower()
                if host == domain:
                    return (3, len(domain))
                if host.endswith("." + domain):
                    return (1, len(domain))
                return (0, 0)
            normalized = site.rstrip("/") + "/"
            return (2, len(normalized)) if blog_url.startswith(normalized) else (0, 0)

        matches = [(score(entry), str(entry.get("siteUrl"))) for entry in verified]
        matches = [match for match in matches if match[0][0] > 0]
        if not matches:
            accessible = ", ".join(str(entry.get("siteUrl")) for entry in verified) or "none"
            raise BloggerError(
                f"No verified GSC property matches {blog_url}; accessible properties: {accessible}"
            )
        return max(matches)[1]

    def submit(self, site_url: str, sitemap_url: str) -> None:
        self.service.sitemaps().submit(siteUrl=site_url, feedpath=sitemap_url).execute()

    def get(self, site_url: str, sitemap_url: str) -> dict:
        return self.service.sitemaps().get(siteUrl=site_url, feedpath=sitemap_url).execute()

    def list_sitemaps(self, site_url: str) -> list[dict]:
        return self.service.sitemaps().list(siteUrl=site_url).execute().get("sitemap", [])

    def delete(self, site_url: str, sitemap_url: str) -> None:
        self.service.sitemaps().delete(siteUrl=site_url, feedpath=sitemap_url).execute()

    def add_site(self, site_url: str) -> None:
        self.service.sites().add(siteUrl=site_url).execute()

    def site(self, site_url: str) -> dict:
        return self.service.sites().get(siteUrl=site_url).execute()


def _credentials(
    client_secret: Path | None,
    token_path: Path,
    scopes: list[str],
    oauth_source: Path | None = None,
) -> Credentials:
    creds = None
    if token_path.exists():
        creds = Credentials.from_authorized_user_file(token_path, scopes)
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    if not creds or not creds.valid:
        if client_secret is not None:
            if not client_secret.exists():
                raise BloggerError(f"OAuth client secret not found: {client_secret}")
            flow = InstalledAppFlow.from_client_secrets_file(client_secret, scopes)
        elif oauth_source and oauth_source.exists():
            source = json.loads(oauth_source.read_text(encoding="utf-8"))
            if not source.get("client_id") or not source.get("client_secret"):
                raise BloggerError(f"OAuth client metadata is missing from: {oauth_source}")
            flow = InstalledAppFlow.from_client_config(
                {
                    "installed": {
                        "client_id": source["client_id"],
                        "client_secret": source["client_secret"],
                        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                        "token_uri": "https://oauth2.googleapis.com/token",
                        "redirect_uris": ["http://localhost"],
                    }
                },
                scopes,
            )
        else:
            raise BloggerError(
                "OAuth token is missing or invalid; provide --client-secret or BLOGGER_CLIENT_SECRET"
            )
        creds = flow.run_local_server(port=0, open_browser=True)
    token_path.write_text(creds.to_json(), encoding="utf-8")
    token_path.chmod(0o600)
    return creds
