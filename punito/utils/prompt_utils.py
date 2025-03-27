from .path_utils import find_resources_path
from .io_utils import read_yaml
from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain_core.messages.base import BaseMessage

def create_messages_from_yaml_template(file_name: str, placeholders: dict) -> list[BaseMessage]:
    """
    Create a list of chat messages from a YAML template file.

    Parameters
    ----------
    file_name : str
        Name of the YAML file (without extension) containing 'system' and 'user' prompt templates.
    placeholders : dict
        Dictionary of placeholder values to format the prompt templates.

    Returns
    -------
    list of BaseMessage
        Formatted system and user chat messages.

    Raises
    ------
    ValueError
        If 'system' or 'user' keys are missing in the YAML file.
    """

    data = read_yaml(find_resources_path() / 'prompts' / (file_name + '.yaml'))

    if "system" not in data or "user" not in data:
        raise ValueError("Prompt YAML must contain both 'system' and 'user' keys.")

    prompt_template = ChatPromptTemplate.from_messages([
        SystemMessagePromptTemplate.from_template(data["system"]),
        HumanMessagePromptTemplate.from_template(data["user"])
    ])

    return prompt_template.format_messages(**placeholders)