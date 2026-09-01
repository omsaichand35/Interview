import re

from .repository import RepositorySnapshot


class DependencyDetector:
    """Detect common project dependencies."""

    def detect(
        self,
        repository: RepositorySnapshot,
    ) -> list[str]:
        """Detect dependencies from repository files."""

        dependencies: set[str] = set()

        for file in repository.files:

            if not file.content:
                continue

            path = file.path.lower()

            if path.endswith(
                "requirements.txt"
            ):
                dependencies.update(
                    self._requirements(
                        file.content
                    )
                )

            elif path.endswith(
                "pyproject.toml"
            ):
                dependencies.update(
                    self._python_project(
                        file.content
                    )
                )

            elif path.endswith(
                "package.json"
            ):
                dependencies.update(
                    self._package_json(
                        file.content
                    )
                )

        return sorted(
            dependencies
        )

    def _requirements(
        self,
        content: str,
    ) -> set[str]:

        result = set()

        for line in content.splitlines():

            line = line.strip()

            if not line or line.startswith("#"):
                continue

            match = re.match(
                r"^([A-Za-z0-9_.-]+)",
                line,
            )

            if match:
                result.add(
                    match.group(1)
                )

        return result

    def _python_project(
        self,
        content: str,
    ) -> set[str]:

        result = set()

        patterns = [
            r'"([A-Za-z0-9_.-]+)"\s*=\s*"',
            r"'([A-Za-z0-9_.-]+)'\s*=\s*'",
        ]

        for pattern in patterns:

            result.update(
                re.findall(
                    pattern,
                    content,
                )
            )

        return result

    def _package_json(
        self,
        content: str,
    ) -> set[str]:

        import json

        try:
            data = json.loads(
                content
            )

        except json.JSONDecodeError:
            return set()

        dependencies = set()

        for field in (
            "dependencies",
            "devDependencies",
        ):
            values = data.get(
                field,
                {},
            )

            dependencies.update(
                values.keys()
            )

        return dependencies