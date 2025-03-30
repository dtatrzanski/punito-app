from pathlib import Path
from loguru import logger
from typing import Any
from langchain_core.runnables import Runnable, RunnableSequence
from langchain_core.runnables.config import RunnableConfig
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


class PromptAndSaveRunnable(Runnable):
    def __init__(self, prompt_name: str, llm, output_key: str,
                 output_dir: Path, filename_fn: callable):
        self.prompt_name = prompt_name
        self.llm = llm
        self.output_key = output_key
        self.output_dir = output_dir
        self.filename_fn = filename_fn

    def invoke(self, input: dict, config: RunnableConfig | None = None, **kwargs: Any) -> dict:
        messages = create_messages_from_yaml_template(self.prompt_name, input)
        output = "".join(chunk.content for chunk in self.llm.stream(messages))

        filename = self.filename_fn(input)
        output_path = self.output_dir / filename
        prompt_path = self.output_dir / "prompts" / f"{self.prompt_name}_{filename}"

        write_to_file(output, output_path)
        write_to_file(get_buffer_string(messages), prompt_path)

        return {**input, self.output_key: output}


class TestsGenerationPipeline:
    def __init__(self, steps_config: dict, llm):
        self.llm = llm
        self.steps_config = steps_config

    def build_pipeline(self, step_names: list, output_dir: Path) -> RunnableSequence:
        runnables = []
        for step_name in step_names:
            config = self.steps_config[step_name]
            prompt = config["prompt"]
            output_key = config["output_var"]
            filename_fn = config["target_filename"]

            runnables.append(PromptAndSaveRunnable(prompt, self.llm, output_key, output_dir, filename_fn))
        return RunnableSequence(*runnables)

    def run(self, flow: list, input: dict, output_dir: Path) -> dict:
        pipeline = self.build_pipeline(flow, output_dir)
        return pipeline.invoke(input)


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

    def _get_common_path(self, fn_name: str) -> Path:
        return self.base_output_path / fn_name

    def generate_plan(self, function_code: str, exe_fn_name: str, tst_fn_name: str) -> str:
        placeholders = {
            "execution_function_name": exe_fn_name,
            "tested_function_name": tst_fn_name,
            "source_code": function_code,
        }
        step_config = self.pipeline_steps["plan"]
        output_dir = self._get_common_path(exe_fn_name)
        runnable = PromptAndSaveRunnable(
            step_config["prompt"],
            self.llm,
            step_config["output_var"],
            output_dir,
            step_config["target_filename"]
        )
        output = runnable.invoke(placeholders)
        return output["tests_plan"]

    def generate_tests(self, function_code: str, exe_fn_name: str, tst_fn_name: str,
                       tests_plan: str, example_code: str = '') -> str:
        placeholders = {
            "execution_function_name": exe_fn_name,
            "tested_function_name": tst_fn_name,
            "source_code": function_code,
            "test_example": example_code,
            "tests_plan": tests_plan,
        }
        step_config = self.pipeline_steps["tests"]
        output_dir = self._get_common_path(exe_fn_name)
        runnable = PromptAndSaveRunnable(
            step_config["prompt"],
            self.llm,
            step_config["output_var"],
            output_dir,
            step_config["target_filename"]
        )
        output = runnable.invoke(placeholders)
        return output["initial_tests"]

    def generate_tests_for_function(self, function_code: str, exe_fn_name: str, tst_fn_name: str,
                                    example_code: str = '') -> str:
        placeholders = {
            "execution_function_name": exe_fn_name,
            "tested_function_name": tst_fn_name,
            "source_code": function_code,
            "test_example": example_code,
        }
        output = self.pipeline.run(["plan", "tests"], placeholders, self._get_common_path(exe_fn_name))
        return output["initial_tests"]

    def generate_tests_for_class(self, class_path: Path) -> None:
        class_code = read_file(class_path)
        logger.info(f"Generating tests for class: {extract_class_name(class_path)}")
        example_path = find_project_root() / "punito" / "resources" / "test_examples" / "PanelControllerExampleMockitoTest.java"
        example_code = read_file(example_path)
        chunked_code = get_chunked_code(class_code)
        for public_fn, deps in chunked_code.items():
            for dep_name, dep_code in deps.items():
                self.generate_tests_for_function(dep_code, public_fn, dep_name, example_code)
