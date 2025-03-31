import argparse
from pathlib import Path

from loguru import logger
from punito.tests_generator import TestsGenerator
from datetime import datetime
from punito.utils import extract_class_name


def main() -> None:
    """
    Entry point for running the test generation via CLI.

    Parses the command-line arguments,
    and starts the process of generating JUnit Mockito tests for the specified Java class.

    It is intended to be used when the module is executed as a script.

    Returns
    -------
    None

    Examples
    --------
    Running the script:

    ```sh
    python -m punito path/to/MyClass.java
    ```
    """

    logger.info("Starting Punito...")
    parser = argparse.ArgumentParser(description="Generate JUnit Mockito tests using deployed model.")
    parser.add_argument("class_path", help="Path to the Java class file.")

    class_path = parser.parse_args().class_path
    logger.info(f"Received arguments: class_path={class_path}")

    generator = TestsGenerator(extract_class_name(class_path), datetime.now().isoformat().replace(":", "-"))
    generator.generate_tests_for_class(class_path=Path(class_path))

if __name__ == "__main__":
    main()
