from pydantic import BaseModel, Field

from .repository import (
    RepositoryFile,
    RepositorySnapshot,
)


class RetrievalRequest(BaseModel):
    """Request for additional repository evidence."""

    reason: str

    file_paths: list[str] = Field(default_factory=list)
    
    priority: str = "normal"


from .github_client import GitHubClient


class ProjectRetriever:
    """Retrieve additional repository evidence."""

    def __init__(self, github_client: GitHubClient):
        self.github_client = github_client
        self.max_file_size = 100_000  # 100 KB limit per file
        self.max_total_retrieved = 1_000_000  # 1 MB total limit
        self.total_retrieved = 0
        self.retrieved_paths: set[str] = set()

    def retrieve(
        self,
        repository: RepositorySnapshot,
        request: RetrievalRequest,
    ) -> list[RepositoryFile]:
        """Retrieve files requested by the analyzer."""

        files_by_path = {
            file.path: file
            for file in repository.files
        }

        retrieved_files = []

        for path in request.file_paths:
            if path not in files_by_path:
                print(f"Skipping unknown path: {path}")
                continue
                
            if path in self.retrieved_paths:
                print(f"Skipping already retrieved path: {path}")
                continue
                
            repo_file = files_by_path[path]
            
            # Simple binary file check by extension
            if self._is_binary(path):
                print(f"Skipping binary file: {path}")
                continue
                
            if repo_file.size > self.max_file_size:
                print(f"Skipping large file: {path} ({repo_file.size} bytes)")
                continue
                
            if self.total_retrieved + repo_file.size > self.max_total_retrieved:
                print(f"Skipping file: {path} due to total content limit")
                continue

            content = self.github_client.fetch_file_content(
                owner=repository.owner,
                repository=repository.name,
                path=path,
                ref=repository.default_branch,
            )
            
            if content is not None:
                repo_file.content = content
                self.retrieved_paths.add(path)
                self.total_retrieved += len(content)
                retrieved_files.append(repo_file)

        return retrieved_files
        
    def _is_binary(self, path: str) -> bool:
        binary_extensions = {
            ".png", ".jpg", ".jpeg", ".gif", ".ico", ".pdf", 
            ".zip", ".tar", ".gz", ".mp4", ".mp3", ".wav", 
            ".exe", ".dll", ".so", ".dylib", ".class", ".pyc"
        }
        return any(path.lower().endswith(ext) for ext in binary_extensions)