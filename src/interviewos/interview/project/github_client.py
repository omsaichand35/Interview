import base64
from urllib.error import HTTPError
from urllib.request import Request, urlopen

import json

from .repository import (
    RepositoryFile,
    RepositorySnapshot,
)

from .repository import RepositoryFile

class GitHubClient:
    """Client for retrieving public GitHub repositories."""

    API_BASE = "https://api.github.com"

    def __init__(
        self,
        token: str | None = None,
    ) -> None:
        self.token = token

    def _request(
        self,
        url: str,
    ) -> dict | list:

        headers = {
            "Accept": "application/vnd.github+json",
            "User-Agent": "InterviewOS",
        }

        if self.token:
            headers[
                "Authorization"
            ] = f"Bearer {self.token}"

        request = Request(
            url,
            headers=headers,
        )

        try:
            with urlopen(request) as response:
                return json.loads(
                    response.read()
                )

        except HTTPError as exc:
            raise RuntimeError(
                f"GitHub API request failed: "
                f"{exc.code} {exc.reason}"
            ) from exc

    def parse_url(
        self,
        repository_url: str,
    ) -> tuple[str, str]:

        cleaned = (
            repository_url
            .rstrip("/")
        )

        parts = cleaned.split("/")

        if len(parts) < 5:
            raise ValueError(
                "Invalid GitHub repository URL."
            )

        if parts[2].lower() != "github.com":
            raise ValueError(
                "URL must point to github.com."
            )

        owner = parts[3]

        repository = parts[4]

        if not owner or not repository:
            raise ValueError(
                "GitHub URL must contain "
                "owner and repository."
            )

        return owner, repository

    def fetch_repository(
        self,
        repository_url: str,
    ) -> RepositorySnapshot:

        owner, repository = self.parse_url(
            repository_url
        )

        repo_data = self._request(
            f"{self.API_BASE}/repos/"
            f"{owner}/{repository}"
        )

        if not isinstance(repo_data, dict):
            repo_data = {}

        tree_data = self._request(
            f"{self.API_BASE}/repos/"
            f"{owner}/{repository}/git/trees/"
            f"{repo_data.get('default_branch', 'main')}"
            "?recursive=1"
        )

        if not isinstance(tree_data, dict):
            tree_data = {}

        files: list[RepositoryFile] = []

        for item in tree_data.get(
            "tree",
            [],
        ):

            if item.get("type") != "blob":
                continue

            path = item.get(
                "path",
                "",
            )

            size = item.get(
                "size",
                0,
            )

            files.append(
                RepositoryFile(
                    path=path,
                    size=size,
                )
            )

        readme = self._fetch_readme(
            owner,
            repository,
        )

        languages = self._request(
            f"{self.API_BASE}/repos/"
            f"{owner}/{repository}/languages"
        )

        if not isinstance(languages, dict):
            languages = {}

        return RepositorySnapshot(
            url=repository_url,
            owner=owner,
            name=repository,
            description=repo_data.get(
                "description"
            ),
            default_branch=repo_data.get(
                "default_branch",
                "main",
            ),
            languages=languages,
            files=files,
            readme=readme,
        )

    def _fetch_readme(
        self,
        owner: str,
        repository: str,
    ) -> str | None:

        try:
            data = self._request(
                f"{self.API_BASE}/repos/"
                f"{owner}/{repository}/readme"
            )

            if not isinstance(data, dict):
                data = {}

        except RuntimeError:
            return None

        encoded = data.get(
            "content"
        )

        if not encoded:
            return None

        encoded = encoded.replace(
            "\n",
            "",
        )

        try:
            return base64.b64decode(
                encoded
            ).decode(
                "utf-8",
                errors="replace",
            )

        except Exception:
            return None

    def fetch_file_content(
            self,
            owner: str,
            repository: str,
            path: str,
            ref: str | None = None,
    ) -> str | None:
        """Fetch the content of a repository file."""

        url = (
            f"{self.API_BASE}/repos/"
            f"{owner}/{repository}/contents/"
            f"{path}"
        )

        if ref:
            url += f"?ref={ref}"

        data = self._request(
            url
        )

        if not isinstance(data, dict):
            return None

        if data.get("type") != "file":
            return None

        encoded = data.get(
            "content"
        )

        if not encoded:
            return None

        encoded = encoded.replace(
            "\n",
            "",
        )

        try:
            return base64.b64decode(
                encoded
            ).decode(
                "utf-8",
                errors="replace",
            )

        except Exception:
            return None

    def enrich_files(
            self,
            snapshot: RepositorySnapshot,
            selected_files: list[RepositoryFile],
    ) -> RepositorySnapshot:
        """Retrieve source for selected files."""

        for file in selected_files:
            content = self.fetch_file_content(
                owner=snapshot.owner,
                repository=snapshot.name,
                path=file.path,
                ref=snapshot.default_branch,
            )

            file.content = content

        return snapshot