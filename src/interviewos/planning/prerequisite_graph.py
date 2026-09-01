from collections import defaultdict, deque
from uuid import UUID


class PrerequisiteGraph:
    """
    Represents relationships between skills/topics using their UUIDs.

    An edge A -> B means A should generally be learned
    before B.
    """

    def __init__(
        self,
        relationships: dict[UUID, list[UUID]] | None = None,
    ) -> None:
        self._graph: dict[UUID, set[UUID]] = defaultdict(set)

        if relationships:
            for topic, prerequisites in relationships.items():
                for prerequisite in prerequisites:
                    self.add_prerequisite(
                        topic=topic,
                        prerequisite=prerequisite,
                    )

    def add_prerequisite(
        self,
        topic: UUID,
        prerequisite: UUID,
    ) -> None:
        """Add a prerequisite relationship."""

        if topic == prerequisite:
            return

        self._graph[topic].add(prerequisite)

    def get_prerequisites(
        self,
        topic: UUID,
    ) -> list[UUID]:
        """Return direct prerequisites for a topic."""
        # Using sorted(key=str) to maintain deterministic ordering
        return sorted(self._graph.get(topic, set()), key=str)

    def get_learning_order(
        self,
        topics: list[UUID],
    ) -> list[UUID]:
        """
        Return topics in prerequisite-first order.

        Only relationships involving the requested topics are
        considered.
        """

        requested_topics = set(topics)

        # Include prerequisites of requested topics.
        all_topics = set(requested_topics)

        for topic in requested_topics:
            all_topics.update(
                self._collect_prerequisites(topic)
            )

        # Build dependency graph.
        dependencies: dict[UUID, set[UUID]] = {
            topic: set()
            for topic in all_topics
        }

        dependents: dict[UUID, set[UUID]] = {
            topic: set()
            for topic in all_topics
        }

        for topic in all_topics:
            for prerequisite in self._graph.get(
                topic,
                set(),
            ):
                if prerequisite in all_topics:
                    dependencies[topic].add(prerequisite)
                    dependents[prerequisite].add(topic)

        # Kahn's topological sorting algorithm.
        queue = deque(
            sorted(
                (topic for topic, deps in dependencies.items() if not deps),
                key=str
            )
        )

        result: list[UUID] = []

        while queue:
            topic = queue.popleft()
            result.append(topic)

            for dependent in sorted(
                dependents[topic], key=str
            ):
                dependencies[dependent].discard(topic)

                if not dependencies[dependent]:
                    queue.append(dependent)

        # A cycle should not silently produce a bad learning path.
        if len(result) != len(all_topics):
            raise ValueError(
                "Circular prerequisite relationship detected."
            )

        # Keep only requested topics in the final result.
        return [
            topic
            for topic in result
            if topic in requested_topics
        ]

    def _collect_prerequisites(
        self,
        topic: UUID,
    ) -> set[UUID]:
        """Recursively collect prerequisites."""

        collected: set[UUID] = set()
        queue = deque([topic])

        while queue:
            current = queue.popleft()

            for prerequisite in self._graph.get(
                current,
                set(),
            ):
                if prerequisite in collected:
                    continue

                collected.add(prerequisite)
                queue.append(prerequisite)

        return collected