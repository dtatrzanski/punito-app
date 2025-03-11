import os
import json
from loguru import logger
from ..llm_client import stream_chat_completion
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

     Notes
     -----
     - The function analyzes the provided Java class code to locate the specified function.
     - It generates test cases based on the function's parameters, return type, and logic.
     - Uses JUnit and Mockito to create test methods
     - The generated tests may involve mocking dependencies if applicable.
     """

    stream_chat_completion(class_code)
    # logger.info(f"Generating tests for function {function_name}")
    #
    # # Construct prompt for the LLM
    # prompt = (
    #     f"Generate tests for the function '{function_name}' "
    #     f"in the following Java class:\n\n{class_code}"
    # )
    #
    # endpoint = "http://bmf-ai.apps.ce.capgemini.com/chat/v1/chat/completions"
    # payload = {
    #     "model": "Llama-3.3-70B-Instruct-AutoRound-GPTQ-4bit",
    #     "messages": [{"role": "user", "content": prompt}],
    #     "stream": True
    # }
    # headers = {"Content-Type": "application/json"}
    #
    # try:
    #     response = requests.post(endpoint, json=payload, headers=headers, stream=True)
    #     response.raise_for_status()
    # except Exception as e:
    #     logger.error(f"Error calling LLM endpoint: {e}")
    #     return
    #
    # output = ""
    #
    # # Stream response chunks
    # for chunk in response.iter_lines():
    #     if chunk:
    #         try:
    #             # If the API returns JSON objects per chunk:
    #             chunk_data = json.loads(chunk.decode("utf-8"))
    #             content = chunk_data.get("choices", [{}])[0].get("delta", {}).get("content", "")
    #             if content:
    #                 logger.info(content)
    #                 output += content
    #         except Exception as e:
    #             logger.error(f"Error processing chunk: {e}")
    #
    # # Save the generated tests into a file
    # try:
    #     script_dir = os.path.dirname(os.path.abspath(__file__))
    #     output_dir = os.path.join(script_dir, "generated_tests")
    #     os.makedirs(output_dir, exist_ok=True)
    #     output_file = os.path.join(output_dir, f"{function_name}_tests.txt")
    #     with open(output_file, "w") as f:
    #         f.write(output)
    #     logger.info(f"Generated tests saved to {output_file}")
    # except Exception as e:
    #     logger.error(f"Error writing output file: {e}")


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

        Notes
        -----
        - Identifies functions in the Java class that require testing.
        - Generates JUnit Mockito tests for each selected function.
        - Combines generated test cases into a single test suite.
        - Runs the test suite and evaluates results.
        - If errors occur, the function iterates to improve test generation.
        """

    # TODO: Implement the orchestration logic for test generation
    # class_code = read_class_file(class_path)
    # generate_tests_for_function(class_code, "function1")