from punito.utils import find_resources_path, read_file

def get_test_example(file_name: str) -> str:
    """Returns example of Mockito test."""

    return read_file(find_resources_path() / "test_examples" / file_name)
