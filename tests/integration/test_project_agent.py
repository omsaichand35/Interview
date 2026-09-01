import pytest
from unittest.mock import Mock, AsyncMock

from interviewos.interview.project.agent import ProjectAnalysisAgent
from interviewos.interview.project.github_client import GitHubClient
from interviewos.interview.project.repository import RepositorySnapshot, RepositoryFile
from interviewos.llm import LLMClient
from interviewos.interview.project.retrieval import RetrievalRequest


@pytest.fixture
def mock_github_client():
    client = Mock(spec=GitHubClient)
    
    # Fake repository snapshot
    snapshot = RepositorySnapshot(
        name="fake-project",
        url="https://github.com/fake/fake-project",
        owner="fake",
        default_branch="main",
        languages={"Python": 100},
        readme="Fake Project with Auth",
        files=[
            RepositoryFile(path="README.md", size=50, content="Fake Project"),
            RepositoryFile(path="requirements.txt", size=20, content="fastapi"),
            RepositoryFile(path="src/main.py", size=100, content="import auth"),
            RepositoryFile(path="src/auth.py", size=200),
            RepositoryFile(path="src/database.py", size=150),
            RepositoryFile(path="src/cache.py", size=50),
        ]
    )
    
    client.fetch_repository.return_value = snapshot
    client.enrich_files.return_value = snapshot  # Assume selector kept some files
    
    def fetch_file_content(owner, repository, path, ref):
        if path == "src/auth.py":
            return "def login(): pass"
        return ""
        
    client.fetch_file_content.side_effect = fetch_file_content
    return client


@pytest.fixture
def mock_llm_client():
    client = AsyncMock(spec=LLMClient)
    
    # We will simulate the LLM responding differently based on the prompt content.
    async def generate_mock(prompt, system_prompt):
        if "Compile the final ProjectProfile" in prompt:
            return '{"repository_name": "fake-project", "repository_url": "fake", "summary": "Final", "analysis_completeness": "COMPLETE"}'
            
        if "Newly Retrieved File Contents:\nFile: src/auth.py" in prompt:
            # Iteration 2: Auth is present, we have sufficient evidence
            return '{"sufficient_evidence": true, "missing_information": [], "retrieval_requests": [], "evidence_discovered": [], "profile_update": {"repository_name": "fake-project", "repository_url": "fake", "summary": "Complete with Auth"}}'
        else:
            # Iteration 1: We are missing auth
            return '{"sufficient_evidence": false, "missing_information": ["auth implementation"], "retrieval_requests": [{"reason": "Need auth", "file_paths": ["src/auth.py"], "priority": "high"}], "evidence_discovered": []}'
            
    async def _generate_structured_wrapper(prompt, model, system_prompt=None, **kwargs):
        import json
        json_str = await generate_mock(prompt, system_prompt)
        return model(**json.loads(json_str))
    client.generate_structured.side_effect = _generate_structured_wrapper
    return client


@pytest.mark.asyncio
async def test_agent_iterative_analysis(mock_llm_client, mock_github_client):
    agent = ProjectAnalysisAgent(llm=mock_llm_client, github_client=mock_github_client)
    
    profile = await agent.analyze("https://github.com/fake/fake-project")
    
    assert profile.repository_name == "fake-project"
    
    # Verify that github_client.fetch_file_content was called for auth.py
    mock_github_client.fetch_file_content.assert_called_once_with(
        owner="fake",
        repository="fake-project",
        path="src/auth.py",
        ref="main"
    )
    
    # LLM generate should have been called at least twice (Iteration 1, Iteration 2)
    assert mock_llm_client.generate_structured.call_count >= 2
