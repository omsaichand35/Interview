from pydantic import BaseModel, Field, field_validator

from interviewos.llm import LLMClient
from .repository import RepositorySnapshot
from .github_client import GitHubClient
from .file_selector import RepositoryFileSelector
from .retrieval import ProjectRetriever, RetrievalRequest
from .profile import ProjectProfile
from .state import ProjectAnalysisState
from .evidence import ProjectEvidence


class IterationResult(BaseModel):
    """Result of an analysis iteration."""
    
    sufficient_evidence: bool = False
    
    missing_information: list[str] = Field(default_factory=list)
    
    retrieval_requests: list[RetrievalRequest] = Field(default_factory=list)
    
    evidence_discovered: list[ProjectEvidence] = Field(default_factory=list)
    
    profile_update: ProjectProfile | None = None

    @field_validator("missing_information", mode="before")
    @classmethod
    def normalize_missing_info(cls, v):
        if not v:
            return []
        if isinstance(v, str):
            return [s.strip() for s in v.split("\n") if s.strip()]
        return v

    @field_validator("retrieval_requests", mode="before")
    @classmethod
    def normalize_retrieval_requests(cls, v):
        if not v:
            return []
        if isinstance(v, list):
            normalized = []
            for item in v:
                if isinstance(item, str):
                    normalized.append(RetrievalRequest(reason="Analysis", file_paths=[item]))
                elif isinstance(item, dict):
                    if "file_paths" not in item:
                        if "file_path" in item:
                            item["file_paths"] = [item.pop("file_path")]
                        elif "path" in item:
                            item["file_paths"] = [item.pop("path")]
                        else:
                            item["file_paths"] = []
                    if "reason" not in item:
                        item["reason"] = "Analysis"
                    normalized.append(item)
                else:
                    normalized.append(item)
            return normalized
        return v

    @field_validator("evidence_discovered", mode="before")
    @classmethod
    def normalize_evidence_discovered(cls, v):
        if not v:
            return []
        if isinstance(v, list):
            res = []
            for item in v:
                if isinstance(item, str):
                    res.append(ProjectEvidence(category="Architecture", description=item))
                elif isinstance(item, dict):
                    cat = item.get("category", "Architecture")
                    desc = item.get("description") or item.get("evidence") or item.get("text") or item.get("summary") or str(item)
                    res.append(ProjectEvidence(category=cat, description=desc, snippet=item.get("snippet"), source_file=item.get("source_file")))
                else:
                    res.append(item)
            return res
        return v

    @field_validator("profile_update", mode="before")
    @classmethod
    def normalize_profile_update(cls, v):
        if not v or v == {}:
            return None
        return v


class ProjectAnalysisAgent:
    """Agentic orchestrator for project analysis."""
    
    SYSTEM_PROMPT = """
You are a senior software engineer acting as an agent to analyze a candidate's GitHub repository.

Your goal is to build a complete, evidence-backed ProjectProfile.
Do not invent anything. Use ONLY the provided evidence.

When you need more information to understand the project architecture, dependencies, or implementation, you MUST request specific files using `retrieval_requests`.
When you have collected enough evidence, set `sufficient_evidence=True` and provide the final `profile_update`.

Distinguish between OBSERVED facts and INFERRED hypotheses in your evidence. Provide short source snippets where relevant.
"""

    def __init__(self, llm: LLMClient, github_client: GitHubClient):
        self.llm = llm
        self.github_client = github_client
        self.retriever = ProjectRetriever(github_client)
        self.file_selector = RepositoryFileSelector()

    async def analyze(self, repository_url: str) -> ProjectProfile:
        """Run the agentic analysis loop."""
        
        print("Project analysis started")
        
        print("Initial repository scan")
        snapshot = self.github_client.fetch_repository(repository_url)
        print(f"Files discovered: {len(snapshot.files)}")
        
        # Initial file selection (without downloading yet, enrich_files downloads)
        selected_files = self.file_selector.select(snapshot.files, limit=10)
        print(f"Relevant files: {len(selected_files)}")
        
        snapshot = self.github_client.enrich_files(snapshot, selected_files)
        
        state = ProjectAnalysisState(
            repository=snapshot,
            files_retrieved=selected_files,
        )
        
        print("Starting iterative analysis...")
        
        while not state.sufficient_evidence and state.iterations < state.max_iterations:
            print(f"Retrieval iteration {state.iterations}")
            
            result = await self._analyze_iteration(state)
            
            state.evidence_discovered.extend(result.evidence_discovered)
            print(f"Evidence discovered: {len(result.evidence_discovered)}")
            
            if result.sufficient_evidence or not result.retrieval_requests:
                print("Analysis complete or no further requests.")
                state.sufficient_evidence = True
                if result.profile_update and result.profile_update.summary and result.profile_update.potential_interview_topics:
                    return self._finalize_profile(result.profile_update, state)
                break
            
            # Perform retrieval
            total_retrieved = 0
            for req in result.retrieval_requests:
                print(f"Requested: {len(req.file_paths)} files (Priority: {req.priority})")
                new_files = self.retriever.retrieve(snapshot, req)
                state.files_retrieved.extend(new_files)
                total_retrieved += len(new_files)
                
            print(f"Retrieved: {total_retrieved} files")
            state.iterations += 1
            
        # Fallback to final compilation if max iterations reached without sufficient evidence
        print("Compiling final profile...")
        return await self._compile_final_profile(state)

    async def _analyze_iteration(self, state: ProjectAnalysisState) -> IterationResult:
        file_list = "\n".join(f.path for f in state.repository.files)
        
        retrieved_content = []
        for f in state.files_retrieved:
            if f.content and f.path not in state.files_analyzed:
                retrieved_content.append(f"File: {f.path}\n```\n{f.content[:1500]}\n```")
                state.files_analyzed.add(f.path)
                
        content_block = "\n\n".join(retrieved_content)
        
        prompt = f"""
Repository: {state.repository.name}
Languages: {state.repository.languages}

All Available Files in Repo:
{file_list}

Newly Retrieved File Contents:
{content_block}

Current Evidence Discovered: {len(state.evidence_discovered)} items.
Iterations: {state.iterations} / {state.max_iterations}

Instructions:
1. Extract concrete architecture, implementation details, libraries, or patterns from the newly retrieved file contents and add them to `evidence_discovered`.
2. If you need more key source files to understand the project, specify them in `retrieval_requests`.
3. If you have enough evidence to understand the project, set `sufficient_evidence=True` and provide a complete `profile_update`.
"""
        return await self.llm.generate_structured(prompt=prompt, system_prompt=self.SYSTEM_PROMPT, model=IterationResult)

    async def _compile_final_profile(self, state: ProjectAnalysisState) -> ProjectProfile:
        all_retrieved_files = "\n".join(
            f"- {f.path} (Size: {f.size} bytes)" for f in state.files_retrieved if f.content
        )
        sample_snippets = []
        for f in state.files_retrieved[:8]:
            if f.content:
                sample_snippets.append(f"### {f.path}\n```\n{f.content[:1000]}\n```")
        code_overview = "\n\n".join(sample_snippets)
        
        evidence_text = "\n".join(
            f"- [{e.category}] {e.description} (File: {e.source_file or 'N/A'})"
            for e in state.evidence_discovered
        ) if state.evidence_discovered else "None"

        prompt = f"""
Compile a comprehensive, accurate, and detailed ProjectProfile for this candidate's repository.

Repository Name: {state.repository.name}
Repository URL: {state.repository.url}
Description: {state.repository.description or 'N/A'}
Languages: {state.repository.languages}
README Content:
{state.repository.readme[:2000] if state.repository.readme else 'N/A'}

Analyzed Files:
{all_retrieved_files}

Key Code Snippets:
{code_overview}

Gathered Evidence:
{evidence_text}

Instructions:
- Provide a clear multi-sentence `summary` of what this project does and how it works.
- List all `languages`, `frameworks`, `libraries`, `technologies`, and `architecture` patterns used.
- List the `important_files` (e.g. entry points, server files, configs).
- Propose concrete `potential_interview_topics` based on the architectural decisions and code implementation.
"""
        profile = await self.llm.generate_structured(prompt=prompt, system_prompt=self.SYSTEM_PROMPT, model=ProjectProfile, max_retries=4)
        return self._finalize_profile(profile, state)
        
    def _finalize_profile(self, profile: ProjectProfile, state: ProjectAnalysisState) -> ProjectProfile:
        if not profile.repository_name:
            profile.repository_name = state.repository.name
        if not profile.repository_url:
            profile.repository_url = state.repository.url
        if not profile.languages and state.repository.languages:
            profile.languages = list(state.repository.languages.keys())
        profile.evidence = state.evidence_discovered
        profile.analysis_completeness = "COMPLETE" if (state.sufficient_evidence or bool(profile.summary)) else "INCOMPLETE"
        return profile
