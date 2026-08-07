"""Google OAuth and Blogger API operations."""

from __future__ import annotations

from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build


SCOPES = ["https://www.googleapis.com/auth/blogger"]


class BloggerError(RuntimeError):
    """Raised when Blogger state is ambiguous or unsafe."""


class BloggerClient:
    def __init__(self, client_secret: Path, token_path: Path):
        self.token_path = token_path
        self.service = build("blogger", "v3", credentials=self._credentials(client_secret))
        self.blog = self._single_blog()

    def _credentials(self, client_secret: Path) -> Credentials:
        creds = None
        if self.token_path.exists():
            creds = Credentials.from_authorized_user_file(self.token_path, SCOPES)
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        if not creds or not creds.valid:
            if not client_secret.exists():
                raise BloggerError(f"OAuth client secret not found: {client_secret}")
            flow = InstalledAppFlow.from_client_secrets_file(client_secret, SCOPES)
            creds = flow.run_local_server(port=0, open_browser=True)
        self.token_path.write_text(creds.to_json(), encoding="utf-8")
        self.token_path.chmod(0o600)
        return creds

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
