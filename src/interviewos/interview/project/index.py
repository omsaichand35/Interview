from collections import defaultdict
from pydantic import BaseModel

from .evidence import ProjectEvidence


class ProjectEvidenceIndex(BaseModel):
    """Lightweight searchable index of project evidence."""
    
    evidence: list[ProjectEvidence]
    
    def search_by_category(self, category: str) -> list[ProjectEvidence]:
        """Find evidence matching a category."""
        category = category.lower()
        return [
            e for e in self.evidence
            if category in e.category.lower()
        ]
        
    def search_by_file(self, file_path: str) -> list[ProjectEvidence]:
        """Find evidence originating from a specific file."""
        return [
            e for e in self.evidence
            if e.source_file and file_path in e.source_file
        ]
        
    def get_all(self) -> list[ProjectEvidence]:
        return self.evidence
