from interviewos.planning import PrerequisiteGraph


def test_prerequisite_order() -> None:
    graph = PrerequisiteGraph(
        {
            "deep learning": ["machine learning"],
            "machine learning": ["python"],
        }
    )

    result = graph.get_learning_order(
        [
            "deep learning",
            "machine learning",
        ]
    )

    assert result == [
        "machine learning",
        "deep learning",
    ]


def test_circular_dependency_is_detected() -> None:
    graph = PrerequisiteGraph(
        {
            "a": ["b"],
            "b": ["a"],
        }
    )

    try:
        graph.get_learning_order(["a"])
        assert False, "Expected circular dependency error"
    except ValueError:
        pass