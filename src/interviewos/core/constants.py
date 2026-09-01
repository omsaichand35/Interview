DEFAULT_PREREQUISITES: dict[str, list[str]] = {
    "machine learning": [
        "python",
        "statistics",
    ],
    "deep learning": [
        "python",
        "machine learning",
    ],
    "computer vision": [
        "python",
        "machine learning",
        "deep learning",
    ],
    "natural language processing": [
        "python",
        "machine learning",
    ],
    "transformers": [
        "deep learning",
        "linear algebra",
        "probability",
    ],
    "pytorch": [
        "python",
        "deep learning",
    ],
    "tensorflow": [
        "python",
        "deep learning",
    ],
    "cuda": [
        "c++",
        "computer architecture",
    ],
    "sql": [
        "database fundamentals",
    ],
    "docker": [
        "linux",
    ],
}