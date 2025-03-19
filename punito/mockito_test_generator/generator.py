from loguru import logger
from ..utils import find_project_root, write_to_file, extract_class_name, get_package_version, create_prompt_from_yaml, \
    read_file, save_json_to_txt
from ..llm_client.streaming_client import stream_chat_completion
import javalang
import json

def get_common_path(class_name: str, exe_fn_name: str, date_time: str):
    return (find_project_root() / 'generated_tests' / get_package_version()
                   / date_time
                   / class_name / 'tests_per_public_function' / f"{exe_fn_name}")

def generate_plan_for_function(function_code: str, class_name: str, exe_fn_name: str, tst_fn_name: str, date_time: str) -> str:
    logger.info(f"Generating plan for testing function {tst_fn_name} by executing {exe_fn_name}")

    common_path = get_common_path(class_name, exe_fn_name, date_time)

    placeholders = {
        "execution_function_name": exe_fn_name,
        "tested_function_name": tst_fn_name,
        "source_code": function_code,
    }

    prompt = create_prompt_from_yaml('planner_prompt', placeholders)

    target_path = common_path / tst_fn_name / f"plan_{tst_fn_name}.txt"
    prompt_path = common_path / tst_fn_name / "prompts" / f"planner_prompt_{tst_fn_name}.txt"

    plan = stream_chat_completion(prompt)
    write_to_file(plan, target_path)
    save_json_to_txt(json.dumps(prompt), prompt_path)

    return plan

def generate_tests_for_function(function_code: str, class_name: str, exe_fn_name: str, tst_fn_name: str, date_time: str,
                                tests_plan: str, example_code='') -> str:
    """
     Generates JUnit Mockito tests for a specified Java function.

     Extracts the given function from the provided Java class code
     and generates corresponding unit tests using JUnit and Mockito.

     Parameters
     ----------
     function_code: str : str
         Source code of the Java function.
     class_name : str
         The name of the class containing the function for which tests will be generated.
     exe_fn_name : str
            The name of the public function which will be executed on each test
     tst_fn_name : str
            Generated tests will be focused on testing this function. If it is a private function, it will be triggered directly or indirectly from the execution function.
     date_time : str
            The date and time when the tests were generated. Should be the same for one chunk.
     tests_plan : str
            The plan for tests generation process including test cases and assertions.
     example_code : str
         Example test to be used in the test generation process.

     Returns
     -------
     None
     """

    logger.info(f"Generating tests for function {tst_fn_name} by executing {exe_fn_name}")

    common_path = get_common_path(class_name, exe_fn_name, date_time)

    target_path = common_path / tst_fn_name / f"{tst_fn_name}.java"
    prompt_path = common_path / tst_fn_name / "prompts" / f"tester_prompt_{tst_fn_name}.txt"

    placeholders = {
        "execution_function_name": exe_fn_name,
        "tested_function_name": tst_fn_name,
        "source_code": function_code,
        "test_example": example_code,
        "tests_plan": tests_plan
    }

    prompt = create_prompt_from_yaml('tester_prompt', placeholders)
    tests = stream_chat_completion(prompt)
    write_to_file(tests, target_path)
    save_json_to_txt(json.dumps(prompt), prompt_path)

    return tests

def generate_review_for_function(function_code: str, class_name: str, exe_fn_name: str, tst_fn_name: str, plan: str, test_code: str, date_time: str) -> str:
    logger.info(f"Generating review for tests of function {tst_fn_name}, triggered by executing {exe_fn_name}")

    common_path = get_common_path(class_name, exe_fn_name, date_time)

    target_path = common_path / tst_fn_name / f"review_{tst_fn_name}.txt"
    prompt_path = common_path / tst_fn_name / "prompts" / f"reviewer_prompt_{tst_fn_name}.txt"

    placeholders = {
        "tested_function_name": exe_fn_name,
        "execution_function_name": tst_fn_name,
        "source_code": function_code,
        "tests_plan": plan,
        "generated_test_code": test_code
    }

    prompt = create_prompt_from_yaml('reviewer_prompt', placeholders)

    write_to_file(stream_chat_completion(prompt), target_path)
    save_json_to_txt(json.dumps(prompt), prompt_path)


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
    # Parse the Java code
    class_code = read_file(class_path)
    tree = javalang.parse.parse(class_code)

    # TODO: Implement the orchestration logic for test generation
    # generate_tests_for_function(read_class_file(class_path), extract_class_name(class_path), "function1")
