from loguru import logger
from datetime import datetime
from ..utils import find_project_root, write_to_file, extract_class_name, get_package_version, create_prompt_from_json
from ..llm_client.streaming_client import stream_chat_completion


def generate_tests_for_function(class_code: str, class_name: str, function_name: str) -> None:
    """
     Generates JUnit Mockito tests for a specified Java function.

     Extracts the given function from the provided Java class code
     and generates corresponding unit tests using JUnit and Mockito.

     Parameters
     ----------
     class_code : str
         The full source code of the Java class as a string.
     class_name : str
         The name of the class containing the function for which tests will be generated.
     function_name : str
         The name of the function for which tests should be generated.

     Returns
     -------
     None
     """

    logger.info(f"Generating tests for function {function_name}")

    target_path = (find_project_root() / 'generated_tests' / get_package_version()
                   / datetime.now().isoformat().replace(":", "-")
                   / "Af200EnergyBasicdataGeneralPanelControllerBean" / 'tests_per_function'
                   / (function_name + ".java"))
    placeholders = {
        "function_name": function_name,
        "source_code": class_code
    }

    prompt = create_prompt_from_json('function_prompt', placeholders)
    write_to_file(stream_chat_completion(prompt), target_path)


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

    class_name = extract_class_name(class_path)
    logger.info(f"Generating tests for class: {class_name}")
    # TODO: Implement the orchestration logic for test generation
    # generate_tests_for_function(read_class_file(class_path), extract_class_name(class_path), "function1")
