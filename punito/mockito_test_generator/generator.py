from loguru import logger
from ..llm_client import stream_chat_completion
from .utils import write_to_file
from pathlib import Path


# from  utils.io_utils import read_class_file

def generate_tests_for_function(class_code: str, function_name: str) -> None:
    """
     Generates JUnit Mockito tests for a specified Java function.

     Extracts the given function from the provided Java class code
     and generates corresponding unit tests using JUnit and Mockito.

     Parameters
     ----------
     class_code : str
         The full source code of the Java class as a string.
     function_name : str
         The name of the function for which tests should be generated.

     Returns
     -------
     None
     """

    tests_for_function = stream_chat_completion(class_code)

    current_file_path = Path(__file__).resolve()

    # Find the root directory (punito)
    root_path = next(p for p in current_file_path.parents if p.name == "punito")

    target_path = root_path / "generated_tests" / "function1"
    logger.debug(target_path)

    write_to_file(tests_for_function, str(target_path))


def generate_tests_for_class(class_path: str) -> None:
    """
        Orchestrates the test generation process for a given Java class.

        Automates the selection of functions to test within the specified Java class,
        generates unit tests for each function, and executes the tests. If errors occur, it reiterates
        the process to refine test generation.

        Parameters
        ----------
        class_path : str
            Path to the Java class file for which tests will be generated.

        Returns
        -------
        None
        """

    # TODO: Implement the orchestration logic for test generation
    # class_code = read_class_file(class_path)
    # generate_tests_for_function(class_code, "function1")
