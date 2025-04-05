from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import List

from loguru import logger
from .pipeline import TestsGenerationPipeline
from .runnables import PromptAndSaveRunnable

from .generator_utils import get_test_example
from ..chat_model import create_llama_model_from_config
from ..processing import get_chunked_code, collect_class_tests
from ..processing.postprocessor import remove_duplicate_tests
from ..utils import (
    find_project_root,
    extract_class_name,
    get_package_version,
    read_file, write_to_file,
)
from ..utils.common_utils import measure_time


class TestsGenerator:
    def __init__(self, class_name: str, date_time: str):
        self.class_name = class_name
        self.date_time = date_time
        self.base_class_output_path = (
                find_project_root()
                / "generated_tests"
                / get_package_version()
                / date_time
                / class_name
        )
        self.base_fn_output_path = self.base_class_output_path / "tests_per_public_function"
        self.llm = create_llama_model_from_config()

        self.pipeline_steps = {
            "plan": {
                "prompt": "planner_prompt",
                "output_var": "tests_plan",
                "target_filename": lambda input: f"plan_{input['tested_function_name']}.txt",
            },
            "tests": {
                "prompt": "tester_prompt",
                "output_var": "initial_tests",
                "target_filename": lambda input: f"{input['tested_function_name']}.java",
            },
        }
        self.pipeline = TestsGenerationPipeline(self.pipeline_steps, self.llm)

    def _set_up_runnable_for_one_step_generation(self, step_config: dict, output_dir: Path) -> PromptAndSaveRunnable:
        return PromptAndSaveRunnable(
            step_config["prompt"],
            self.llm,
            step_config["output_var"],
            output_dir,
            step_config["target_filename"]
        )

    def _get_common_output_path(self, fn_name: str) -> Path:
        return self.base_fn_output_path / fn_name

    def generate_plan(self, function_code: str, exe_fn_name: str, tst_fn_name: str, prompt="planner_prompt") -> str:
        placeholders = {
            "execution_function_name": exe_fn_name,
            "tested_function_name": tst_fn_name,
            "source_code": function_code,
        }

        plan_step = {
            "prompt": prompt,
            "output_var": "tests_plan",
            "target_filename": lambda input: f"plan_{input['tested_function_name']}.txt",
        }

        runnable = self._set_up_runnable_for_one_step_generation(plan_step,
                                                                 self._get_common_output_path(exe_fn_name))
        return runnable.invoke(placeholders)["tests_plan"]

    def generate_tests(self, function_code: str, exe_fn_name: str, tst_fn_name: str,
                       tests_plan: str, example_code: str = '') -> str:
        placeholders = {
            "execution_function_name": exe_fn_name,
            "tested_function_name": tst_fn_name,
            "source_code": function_code,
            "test_example": example_code,
            "tests_plan": tests_plan,
        }

        runnable = self._set_up_runnable_for_one_step_generation(self.pipeline_steps["tests"],
                                                                 self._get_common_output_path(exe_fn_name))
        return runnable.invoke(placeholders)["initial_tests"]

    def generate_tests_for_chunk(self, function_code: str, exe_fn_name: str, tst_fn_name: str,
                                 example_code: str = '', steps=None) -> str:
        if steps is None:
            steps = ["plan", "tests"]

        placeholders = {
            "execution_function_name": exe_fn_name,
            "tested_function_name": tst_fn_name,
            "source_code": function_code,
            "test_example": example_code,
        }

        logger.info(f"Pipeline execution started | Test function: {tst_fn_name} | Execution function: {exe_fn_name}")
        output = self.pipeline.run(steps, placeholders, self._get_common_output_path(exe_fn_name))

        return output["initial_tests"]

    @measure_time
    def generate_tests_for_class(self, class_path: Path) -> None:
        class_code = read_file(class_path)
        example_code = get_test_example("PanelControllerExampleMockitoTest.java")
        chunked_code = get_chunked_code(class_code)

        logger.info(f"Generating tests for class: {extract_class_name(class_path)}")

        results = []

        with ThreadPoolExecutor(max_workers=50) as executor:
            futures = [
                executor.submit(
                    self.generate_tests_for_chunk,
                    dep_code, public_fn, dep_name, example_code
                )
                for public_fn, deps in chunked_code.items()
                for dep_name, dep_code in deps.items()
            ]

            for future in as_completed(futures):
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    logger.error(f"Test generation failed: {e}")

        test = collect_class_tests(results, extract_class_name(class_path))

        final_test = remove_duplicate_tests(test)

        write_to_file(final_test, self.base_class_output_path / f"{self.class_name}MockitoTest" )
