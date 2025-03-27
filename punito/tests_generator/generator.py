import javalang
from pathlib import Path
from loguru import logger
from langchain_core.messages import get_buffer_string

from ..utils import (
    find_project_root,
    write_to_file,
    extract_class_name,
    get_package_version,
    create_messages_from_yaml_template,
    read_file,
)
from ..chat_model import create_llama_model_from_config

class TestsGenerator:
    def __init__(self, class_name: str, date_time: str):
        self.class_name = class_name
        self.date_time = date_time
        self.base_output_path = (
            find_project_root()
            / 'generated_tests'
            / get_package_version()
            / date_time
            / class_name
            / 'tests_per_public_function'
        )
        self.llm = create_llama_model_from_config(True)

    def _get_common_path(self, exe_fn_name: str) -> Path:
        return self.base_output_path / exe_fn_name

    def _generate(self, exe_fn_name: str, tst_fn_name: str, prompt_name: str, placeholders: dict, filename: str) -> str:
        logger.info(f"{prompt_name} for {tst_fn_name} using {exe_fn_name}")
        common_path = self._get_common_path(exe_fn_name)
        target_path = common_path / tst_fn_name / filename
        prompt_path = common_path / tst_fn_name / "prompts" / f"{prompt_name}_{tst_fn_name}.txt"

        messages = create_messages_from_yaml_template(prompt_name, placeholders)

        output = ""
        for chunk in self.llm.stream(messages):
            token = chunk.content
            print(token, end="", flush=True)
            output += token

        write_to_file(output, target_path)
        write_to_file(get_buffer_string(messages), prompt_path)

        return output

    def generate_plan(self, function_code: str, exe_fn_name: str, tst_fn_name: str) -> str:
        placeholders = {
            "execution_function_name": exe_fn_name,
            "tested_function_name": tst_fn_name,
            "source_code": function_code,
        }
        return self._generate(exe_fn_name, tst_fn_name, 'planner_prompt', placeholders, f"plan_{tst_fn_name}.txt")

    def generate_tests(self, function_code: str, exe_fn_name: str, tst_fn_name: str,
                       tests_plan: str, example_code: str = '') -> str:
        placeholders = {
            "execution_function_name": exe_fn_name,
            "tested_function_name": tst_fn_name,
            "source_code": function_code,
            "test_example": example_code,
            "tests_plan": tests_plan,
        }
        return self._generate(exe_fn_name, tst_fn_name, 'tester_prompt', placeholders, f"initial_{tst_fn_name}.java")

    def generate_review(self, function_code: str, exe_fn_name: str, tst_fn_name: str, test_code: str) -> str:
        placeholders = {
            "tested_function_name": exe_fn_name,
            "execution_function_name": tst_fn_name,
            "source_code": function_code,
            "generated_test_code": test_code,
        }
        return self._generate(exe_fn_name, tst_fn_name, 'reviewer_prompt', placeholders, f"review_{tst_fn_name}.txt")

    def generate_refined_tests(self, exe_fn_name: str, tst_fn_name: str, tests: str, review_report: str) -> str:
        placeholders = {
            "execution_function_name": exe_fn_name,
            "tested_function_name": tst_fn_name,
            "generated_test_code": tests,
            "review_report": review_report,
        }
        return self._generate(exe_fn_name, tst_fn_name, 'refiner_prompt', placeholders, f"{tst_fn_name}.java")

    def generate_tests_for_function(self, function_code: str, exe_fn_name: str, tst_fn_name: str,
                                    example_code: str = '') -> str:
        """
        Full pipeline for generating refined tests for a single function.
        1. Generate test plan
        2. Generate initial tests
        3. Generate review
        4. Generate refined tests
        """
        plan = self.generate_plan(function_code, exe_fn_name, tst_fn_name)
        initial_tests = self.generate_tests(function_code, exe_fn_name, tst_fn_name, plan, example_code)
        review = self.generate_review(function_code, exe_fn_name, tst_fn_name, initial_tests)
        final_tests = self.generate_refined_tests(exe_fn_name, tst_fn_name, initial_tests, review)

        return final_tests

    def generate_tests_for_class(class_path: str, date_time: str) -> None:
        """
        Orchestrates the test generation process for a given Java class.

        Parameters
        ----------
        class_path : str
            Path to the Java class file for which tests will be generated.
        date_time : str
            Timestamp string for organizing output.
        """
        path = Path(class_path)
        class_name = extract_class_name(path)
        logger.info(f"Generating tests for class: {class_name}")

        class_code = read_file(path)
        tree = javalang.parse.parse(class_code)

        # TODO: Implement orchestration logic for extracting public/private methods
        # and calling generate_plan, generate_tests, etc., as needed.


