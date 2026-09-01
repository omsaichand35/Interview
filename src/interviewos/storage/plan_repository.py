import json
from abc import ABC, abstractmethod
from pathlib import Path
from uuid import UUID

from interviewos.models.plan import PreparationPlan


class PlanRepository(ABC):
    """Abstract base class for PreparationPlan storage."""

    @abstractmethod
    def save(self, plan: PreparationPlan) -> None:
        """Save a PreparationPlan."""
        pass

    @abstractmethod
    def get(self, plan_id: UUID) -> PreparationPlan | None:
        """Retrieve a PreparationPlan by ID."""
        pass

    @abstractmethod
    def list_all(self) -> list[PreparationPlan]:
        """List all available PreparationPlans."""
        pass


class JSONPlanRepository(PlanRepository):
    """Stores PreparationPlans as JSON files in a directory."""

    def __init__(self, storage_dir: Path) -> None:
        self.storage_dir = storage_dir
        self.storage_dir.mkdir(parents=True, exist_ok=True)

    def save(self, plan: PreparationPlan) -> None:
        file_path = self.storage_dir / f"{plan.id}.json"
        
        # Pydantic v2 serialization
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(plan.model_dump_json(indent=2))

    def get(self, plan_id: UUID) -> PreparationPlan | None:
        file_path = self.storage_dir / f"{plan_id}.json"
        
        if not file_path.exists():
            return None
            
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            return PreparationPlan.model_validate(data)

    def list_all(self) -> list[PreparationPlan]:
        plans = []
        for file_path in self.storage_dir.glob("*.json"):
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    plans.append(PreparationPlan.model_validate(data))
            except Exception:
                # Skip invalid files
                continue
        return plans
