from interviewos.analysis import SkillGapAnalyzer
from interviewos.models import (
    JobProfile,
    ResumeProfile,
    Skill,
    SkillLevel,
    SkillRequirement,
)


def test_skill_gap_detects_missing_skill() -> None:
    resume = ResumeProfile(
        candidate_name="Test Candidate",
        skills=[
            Skill(
                name="Python",
                level=SkillLevel.ADVANCED,
                evidence=["Built Python applications."],
            )
        ],
    )

    job = JobProfile(
        title="AI Engineer",
        required_skills=[
            SkillRequirement(
                name="Python",
                expected_level=SkillLevel.ADVANCED,
                importance=1.0,
            ),
            SkillRequirement(
                name="PyTorch",
                expected_level=SkillLevel.INTERMEDIATE,
                importance=0.9,
            ),
        ],
    )

    analyzer = SkillGapAnalyzer()

    report = analyzer.analyze(
        resume=resume,
        job=job,
    )

    assert len(report.missing_skills) == 1
    assert report.missing_skills[0].name == "PyTorch"