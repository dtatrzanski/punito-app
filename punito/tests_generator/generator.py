from pathlib import Path
from loguru import logger
from langchain_core.messages import get_buffer_string

from ..processing import get_chunked_code
from ..utils import (
    find_project_root,
    write_to_file,
    extract_class_name,
    get_package_version,
    create_messages_from_yaml_template,
    read_file,
)
from ..chat_model import create_llama_model_from_config

# LCELPipeline enables chaining LCEL steps.
class LCELPipeline:
    def __init__(self, steps: dict, llm):
        """
        steps: Mapping of step names to their configuration.
        llm: Language model instance for processing prompts.
        """
        self.steps = steps
        self.llm = llm

    def run(self, flow: list, inputs: dict, base_output_path: Path = None) -> dict:
        data = inputs.copy()
        for step_name in flow:
            step = self.steps.get(step_name)
            if step is None:
                raise ValueError(f"Step '{step_name}' not defined.")
            prompt_name = step["prompt"]
            output_var = step["output_var"]
            target_filename = step.get("target_filename")

            logger.info(f"Executing step '{step_name}' with prompt '{prompt_name}'")
            messages = create_messages_from_yaml_template(prompt_name, data)
            output = ""
            for chunk in self.llm.stream(messages):
                token = chunk.content
                print(token, end="", flush=True)
                output += token
            data[output_var] = output

            if base_output_path and target_filename:
                filename = target_filename(data) if callable(target_filename) else target_filename
                logger.debug(f"path to write is: {base_output_path / filename}")
                step_path = base_output_path / filename
                write_to_file(output, step_path)
                prompt_path = base_output_path / "prompts" / f"{prompt_name}_{filename}"
                write_to_file(get_buffer_string(messages), prompt_path)
        return data

class TestsGenerator:
    def __init__(self, class_name: str, date_time: str):
        self.class_name = class_name
        self.date_time = date_time
        self.base_output_path = (
            find_project_root()
            / "generated_tests"
            / get_package_version()
            / date_time
            / class_name
            / "tests_per_public_function"
        )
        self.llm = create_llama_model_from_config(True)
        # Define LCEL pipeline steps for test plan and tests generation.
        self.pipeline_steps = {
            "plan": {
                "prompt": "planner_prompt",
                "output_var": "plan_output",
                "target_filename": lambda inputs: f"plan_{inputs['tested_function_name']}.txt",
            },
            "tests": {
                "prompt": "tester_prompt",
                "output_var": "tests_output",
                "target_filename": lambda inputs: f"{inputs['tested_function_name']}.java",
            },
            # Additional steps (review, refinement, etc.) can be added here.
        }
        self.pipeline = LCELPipeline(self.pipeline_steps, self.llm)

    def _get_common_path(self, exe_fn_name: str, tst_fn_name: str) -> Path:
        return self.base_output_path / exe_fn_name / tst_fn_name

    def generate_plan(self, function_code: str, exe_fn_name: str, tst_fn_name: str) -> str:
        """
        Generates a test plan for a given function.
        """
        placeholders = {
            "execution_function_name": exe_fn_name,
            "tested_function_name": tst_fn_name,
            "source_code": function_code,
        }
        common_path = self._get_common_path(exe_fn_name, tst_fn_name)
        result = self.pipeline.run(flow=["plan"], inputs=placeholders, base_output_path=common_path)
        return result["plan_output"]

    def generate_tests(self, function_code: str, exe_fn_name: str, tst_fn_name: str,
                       tests_plan: str, example_code: str = '') -> str:
        """
        Generates tests using the provided test plan.
        """
        placeholders = {
            "execution_function_name": exe_fn_name,
            "tested_function_name": tst_fn_name,
            "source_code": function_code,
            "test_example": example_code,
            "tests_plan": tests_plan,
        }
        common_path = self._get_common_path(exe_fn_name, tst_fn_name)
        result = self.pipeline.run(flow=["tests"], inputs=placeholders, base_output_path=common_path)
        return result["tests_output"]

    def generate_tests_for_function(self, function_code: str, exe_fn_name: str, tst_fn_name: str,
                                    example_code: str = '') -> str:
        """
        Full pipeline: generate test plan then tests.
        """
        placeholders = {
            "execution_function_name": exe_fn_name,
            "tested_function_name": tst_fn_name,
            "source_code": function_code,
            "test_example": example_code,
        }
        common_path = self._get_common_path(exe_fn_name, tst_fn_name)
        result = self.pipeline.run(flow=["plan", "tests"], inputs=placeholders, base_output_path=common_path)
        return result["tests_output"]

    def generate_tests_for_class(self, class_path: Path) -> None:
        """
        Orchestrates the test generation process for a given Java class.
        """
        class_code = read_file(class_path)
        logger.info(f"Generating tests for class: {extract_class_name(class_path)}")
        example_path = find_project_root() / "punito" / "resources" / "test_examples" / "PanelControllerExampleMockitoTest.java"
        example_code = read_file(example_path)
        chunked_code = get_chunked_code(class_code)
        for public_function, dependencies in chunked_code.items():
            for dep_name, dep_code in dependencies.items():
                self.generate_tests_for_function(dep_code, public_function, dep_name, example_code)
