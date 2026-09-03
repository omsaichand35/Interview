from interviewos.llm import (
    LLMClient,
)
from .dependencies import DependencyDetector

from .profile import ProjectProfile
from .repository import RepositorySnapshot


class ProjectAnalyzer:
    """Analyze a repository into a project profile."""

    SYSTEM_PROMPT = """
You are a senior software engineer analyzing
a candidate's GitHub repository for an interview.

Your job is to identify what the project actually
contains based on repository evidence.

Do not invent technologies or architecture.

Only claim something when the repository provides
reasonable evidence.

Your analysis must be evidence-grounded.

Rules:

1. Do not invent technologies.
2. Do not claim a framework is used unless repository
   evidence supports it.
3. Do not assume the candidate personally authored
   every file.
4. Distinguish repository facts from reasonable inference.
5. Cite important repository files when describing
   architecture or implementation.
6. Identify contradictions when README claims differ
   from the source code.
7. Identify technologies that appear in dependencies
   but are not visibly used.
8. Identify important implementation decisions that
   could be discussed during an interview.
9. Suggest interview topics based on actual evidence.
10. Do not make hiring decisions.

Identify:

- project purpose
- programming languages
- frameworks
- libraries
- technologies
- architecture
- important files
- testing approach
- deployment approach
- potential technical interview topics

Separate observed evidence from inference.

Return only structured output.
"""

    def __init__(
            self,
            llm: LLMClient,
    ) -> None:
        self.llm = llm

        self.dependency_detector = (
            DependencyDetector()
        )

    async def analyze(
        self,
        repository: RepositorySnapshot,
    ) -> ProjectProfile:
        """Analyze a repository snapshot."""

        file_list = "\n".join(
            file.path
            for file in repository.files
        )

        prompt = f"""
Repository:

Name: {repository.name}
URL: {repository.url}
Description: {repository.description}
Languages: {repository.languages}

README:

{repository.readme or "No README found."}

Repository files:

{file_list}

Analyze the repository and return a JSON object matching this exact structure:

{{
    "repository_name": "{repository.name}",
    "repository_url": "{repository.url}",
    "summary": "A machine learning pipeline for image classification using PyTorch with REST API backend",
    "languages": ["Python", "JavaScript"],
    "frameworks": ["PyTorch", "Flask", "React"],
    "libraries": ["NumPy", "Pandas", "Scikit-learn", "OpenCV"],
    "architecture": ["MVC", "REST API", "Neural Network Pipeline"],
    "technologies": ["Docker", "PostgreSQL", "Redis", "AWS S3"],
    "important_files": ["models/classifier.py", "api/server.py", "preprocessing/pipeline.py"],
    "testing_approach": "pytest with unit tests and integration tests",
    "deployment_approach": "Docker containerization with AWS deployment",
    "database_usage": "PostgreSQL for metadata and caching with Redis",
    "external_services": ["AWS S3 for model storage", "third-party API for data augmentation"],
    "architectural_decisions": [
        "Used PyTorch instead of TensorFlow for flexibility",
        "REST API for easy integration with frontend",
        "Redis caching for prediction results"
    ],
    "potential_interview_topics": [
        "Neural network architecture design decisions",
        "Performance optimization techniques",
        "API design and scalability",
        "Data pipeline and preprocessing",
        "Deployment and DevOps considerations"
    ],
    "evidence": [],
    "unresolved_areas": ["Details about training pipeline configuration"],
    "analysis_completeness": "COMPLETE"
}}

IMPORTANT: 
- Only include technologies/frameworks actually visible in the repository
- Cite file paths as evidence
- Return ONLY valid JSON, no markdown or schema metadata
"""

        return await self.llm.generate_structured(
            prompt=prompt,
            system_prompt=self.SYSTEM_PROMPT,
            model=ProjectProfile
        )