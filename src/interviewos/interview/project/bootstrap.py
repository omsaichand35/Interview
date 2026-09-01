from interviewos.interview.project.agent import ProjectAnalysisAgent
from .github_client import GitHubClient
from .file_selector import RepositoryFileSelector
from .profile import ProjectProfile


class ProjectInterviewBootstrap:
    """Prepare project context for an interview."""

    def __init__(
        self,
        github_client: GitHubClient,
        agent: ProjectAnalysisAgent,
    ) -> None:
        self.github_client = github_client
        self.agent = agent

    async def prepare(
        self,
        repository_url: str,
    ) -> ProjectProfile:
        """Analyze a candidate repository."""
        
        return await self.agent.analyze(repository_url)