from pathlib import Path
from typing import Any
from langchain_core.messages import get_buffer_string
from langchain_core.runnables import Runnable, RunnableConfig

from punito.utils import create_messages_from_yaml_template, write_to_file


class PromptAndSaveRunnable(Runnable):
    """
    Runnable that generates output using an LLM, saves the result and prompt to disk, and returns output in a dictionary.

    Parameters
    ----------
    prompt_name : str
        Name of the YAML prompt template.
    llm : Any
        Large language model instance.
    output_key : str
        Key under which to store the generated output in the returned dictionary.
    output_dir : Path
        Directory where output and prompts will be saved.
    filename_fn : callable
        Function that takes `params` as input and returns a filename string.
    """

    def __init__(self, prompt_name: str, llm, output_key: str,
                 output_dir: Path, filename_fn: callable):
        self.prompt_name = prompt_name
        self.llm = llm
        self.output_key = output_key
        self.output_dir = output_dir
        self.filename_fn = filename_fn

    def invoke(self, params: dict, config: RunnableConfig | None = None, **kwargs: Any) -> dict:
        """
        Generate and save output from an LLM using a prompt template and input parameters.

        Parameters
        ----------
        params : dict
            Input parameters for prompt.
        config : RunnableConfig, optional
            Configuration for the Runnable interface.
        **kwargs : Any
            Additional arguments.

        Returns
        -------
        dict
            Dictionary combining original `params` with an additional key (`output_key`)
            containing the generated output string, which can be used in next step in the pipeline.
        """

        messages = create_messages_from_yaml_template(self.prompt_name, params)
        output = self.llm.invoke(messages, config=config).content

        filename = self.filename_fn(params)
        output_path = self.output_dir / filename
        prompt_path = self.output_dir / "prompts" / f"{self.prompt_name}_{filename}"

        write_to_file(output, output_path)
        write_to_file(get_buffer_string(messages), prompt_path)

        return {**params, self.output_key: output}