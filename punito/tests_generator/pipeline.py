from pathlib import Path
from langchain_core.runnables import RunnableSequence

from punito.tests_generator.runnables import PromptAndSaveRunnable


class TestsGenerationPipeline:
    """
    Pipeline for generating test-related artifacts using an LLM and a sequence of prompt-based steps.

    Parameters
    ----------
    steps_config : dict
        Dictionary mapping step names to their configuration. Each configuration must include:
        - "prompt": Name of the prompt template.
        - "output_var": Key to store generated output.
        - "target_filename": Callable that returns the output filename.
    llm : Any
        Large language model instance.
    """

    def __init__(self, steps_config: dict, llm):
        self.llm = llm
        self.steps_config = steps_config

    def build_pipeline(self, step_names: list, output_dir: Path) -> RunnableSequence:
        """
        Build a sequence of runnable steps based on configuration.

        Parameters
        ----------
        step_names : list
            A list of step names to include in the pipeline, in execution order.
        output_dir : Path
            Directory where each step will save its generated output and prompt.

        Returns
        -------
        RunnableSequence
            A composed pipeline of `PromptAndSaveRunnable` instances.
        """
        runnables = []
        for step_name in step_names:
            config = self.steps_config[step_name]
            prompt = config["prompt"]
            output_key = config["output_var"]
            filename_fn = config["target_filename"]

            runnables.append(PromptAndSaveRunnable(prompt, self.llm, output_key, output_dir, filename_fn))
        return RunnableSequence(*runnables)

    def run(self, flow: list, params: dict, output_dir: Path) -> dict:
        """
        Execute the pipeline using a list of step names and input parameters.

        Parameters
        ----------
        flow : list
            Ordered list of step names to run.
        params : dict
            Initial parameters passed to the first step (placeholders for the first prompt).
        output_dir : Path
            Directory to which outputs and prompts will be saved.

        Returns
        -------
        dict
            Dictionary with cumulative outputs from all steps, including initial `params`.
        """

        pipeline = self.build_pipeline(flow, output_dir)
        return pipeline.invoke(params)
