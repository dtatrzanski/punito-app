from pathlib import Path
from loguru import logger

from punito.processing import collect_class_tests
from dev_utils import collect_chunks, get_latest_artifact_path


from punito.utils import write_to_file


def main() -> None:
    """
    Script for testing collection of tests.
    """

    artifact = get_latest_artifact_path()
    chunks = collect_chunks(artifact)
    test_class = f"{(next(artifact.iterdir(), None)).name}"
    final_test = collect_class_tests(chunks, test_class)

    write_to_file(final_test, Path(__file__).parent / "debug" / "latest" / "collect_tests" / f"{test_class}MockitoTest.java")


if __name__ == "__main__":
    main()
