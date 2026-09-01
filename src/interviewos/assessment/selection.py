from interviewos.models import (
    AssessmentSession,
    CandidateSelection,
    SelectionPolicy,
    SelectionResult,
    SelectionStatus,
)


class SelectionEngine:
    """Select candidates from completed assessment sessions."""

    def select(
        self,
        sessions: list[AssessmentSession],
        policy: SelectionPolicy,
    ) -> SelectionResult:
        """Apply selection policy to assessment results."""

        completed = [
            session
            for session in sessions
            if session.result is not None
        ]

        selections: list[
            CandidateSelection
        ] = []

        for session in completed:

            result = session.result

            reasons: list[str] = []

            eligible = (
                result.score
                >= policy.minimum_score
            )

            if eligible:
                reasons.append(
                    "Overall score meets "
                    "the minimum threshold."
                )
            else:
                reasons.append(
                    "Overall score is below "
                    "the minimum threshold."
                )

            if (
                policy.require_topic_thresholds
            ):
                for topic, threshold in (
                    policy.topic_thresholds.items()
                ):
                    topic_score = next(
                        (
                            score
                            for score
                            in result.topic_scores
                            if score.topic.lower()
                            == topic.lower()
                        ),
                        None,
                    )

                    if topic_score is None:
                        eligible = False

                        reasons.append(
                            f"Missing required topic: "
                            f"{topic}."
                        )

                        continue

                    if (
                        topic_score.score
                        < threshold
                    ):
                        eligible = False

                        reasons.append(
                            f"{topic} score is below "
                            f"the required threshold."
                        )

            status = (
                SelectionStatus.ELIGIBLE
                if eligible
                else SelectionStatus.INELIGIBLE
            )

            selections.append(
                CandidateSelection(
                    candidate_id=(
                        session.candidate_id
                    ),
                    assessment_id=(
                        session.assessment_id
                    ),
                    score=result.score,
                    status=status,
                    reasons=reasons,
                )
            )

        eligible = [
            selection
            for selection in selections
            if selection.status
            == SelectionStatus.ELIGIBLE
        ]

        eligible.sort(
            key=lambda selection: selection.score,
            reverse=True,
        )

        for rank, selection in enumerate(
            eligible,
            start=1,
        ):
            selection.rank = rank

        if policy.maximum_candidates is not None:
            shortlisted = eligible[
                : policy.maximum_candidates
            ]
        else:
            shortlisted = eligible

        shortlisted_ids = {
            selection.candidate_id
            for selection in shortlisted
        }

        for selection in selections:

            if (
                selection.candidate_id
                in shortlisted_ids
            ):
                selection.status = (
                    SelectionStatus.SHORTLISTED
                )

            elif (
                selection.status
                == SelectionStatus.ELIGIBLE
            ):
                selection.status = (
                    SelectionStatus.REJECTED
                )

        return SelectionResult(
            selections=selections,
            shortlisted_candidate_ids=[
                selection.candidate_id
                for selection in shortlisted
            ],
        )