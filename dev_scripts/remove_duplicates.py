from pathlib import Path

from punito.processing import collect_class_tests
from dev_utils import collect_chunks, get_latest_artifact_path
from punito.processing.postprocessor import remove_duplicate_tests

from punito.utils import write_to_file


def main() -> None:
    """
    Script for testing removal of tests duplicates.
    """

    artifact = get_latest_artifact_path()
    chunks = collect_chunks(artifact)
    test_class = f"{(next(artifact.iterdir(), None)).name}MockitoTest"
    test = collect_class_tests(chunks, test_class)

    final_test = remove_duplicate_tests(test)
    write_to_file(final_test, Path(__file__).parent / "debug" / "latest" / "remove_duplicates" / f"{test_class}.java")


if __name__ == "__main__":
    main()




