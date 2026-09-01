import pytest
from unittest.mock import Mock, MagicMock

from interviewos.interview.project.github_client import GitHubClient
from interviewos.interview.project.repository import RepositorySnapshot, RepositoryFile
from interviewos.interview.project.retrieval import ProjectRetriever, RetrievalRequest


@pytest.fixture
def mock_github_client():
    client = Mock(spec=GitHubClient)
    client.fetch_file_content.return_value = "mocked content"
    return client


@pytest.fixture
def retriever(mock_github_client):
    return ProjectRetriever(github_client=mock_github_client)


@pytest.fixture
def repository():
    return RepositorySnapshot(
        name="test-repo",
        url="https://github.com/test/test-repo",
        owner="test",
        default_branch="main",
        files=[
            RepositoryFile(path="src/main.py", size=100),
            RepositoryFile(path="src/large.py", size=200_000),  # Exceeds max_file_size
            RepositoryFile(path="image.png", size=500),         # Binary
        ]
    )


def test_retrieval_success(retriever, repository, mock_github_client):
    req = RetrievalRequest(reason="test", file_paths=["src/main.py"])
    retrieved = retriever.retrieve(repository, req)
    
    assert len(retrieved) == 1
    assert retrieved[0].path == "src/main.py"
    assert retrieved[0].content == "mocked content"
    mock_github_client.fetch_file_content.assert_called_once_with(
        owner="test",
        repository="test-repo",
        path="src/main.py",
        ref="main"
    )


def test_reject_unknown_path(retriever, repository):
    req = RetrievalRequest(reason="test", file_paths=["unknown.py"])
    retrieved = retriever.retrieve(repository, req)
    assert len(retrieved) == 0


def test_reject_binary_file(retriever, repository):
    req = RetrievalRequest(reason="test", file_paths=["image.png"])
    retrieved = retriever.retrieve(repository, req)
    assert len(retrieved) == 0


def test_reject_large_file(retriever, repository):
    req = RetrievalRequest(reason="test", file_paths=["src/large.py"])
    retrieved = retriever.retrieve(repository, req)
    assert len(retrieved) == 0


def test_duplicate_prevention(retriever, repository, mock_github_client):
    req = RetrievalRequest(reason="test", file_paths=["src/main.py"])
    
    # First request
    retrieved1 = retriever.retrieve(repository, req)
    assert len(retrieved1) == 1
    
    # Second request
    retrieved2 = retriever.retrieve(repository, req)
    assert len(retrieved2) == 0
    
    # Called only once
    mock_github_client.fetch_file_content.assert_called_once()


def test_total_retrieved_limit(retriever, repository, mock_github_client):
    # Setup mock content to be exactly max limit
    mock_github_client.fetch_file_content.return_value = "x" * 1_000_000
    
    req1 = RetrievalRequest(reason="test", file_paths=["src/main.py"])
    retrieved1 = retriever.retrieve(repository, req1)
    assert len(retrieved1) == 1
    assert retriever.total_retrieved == 1_000_000
    
    # Second request should fail total limit
    repository.files.append(RepositoryFile(path="src/other.py", size=100))
    req2 = RetrievalRequest(reason="test", file_paths=["src/other.py"])
    retrieved2 = retriever.retrieve(repository, req2)
    assert len(retrieved2) == 0
