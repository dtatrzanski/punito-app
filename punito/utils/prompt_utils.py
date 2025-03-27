from .path_utils import find_resources_path
from .io_utils import read_yaml
from loguru import logger
from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain_core.messages.base import BaseMessage

def create_prompt_from_yaml(file_name: str, placeholders: dict) -> list[BaseMessage]:
    data = read_yaml(find_resources_path() / 'prompts' / (file_name + '.yaml'))

    if "system" not in data or "user" not in data:
        raise ValueError("Prompt YAML must contain both 'system' and 'user' keys.")

    prompt_template = ChatPromptTemplate.from_messages([
        SystemMessagePromptTemplate.from_template(data["system"]),
        HumanMessagePromptTemplate.from_template(data["user"])
    ])

    return prompt_template.format_messages(**placeholders)

def map_prompt_to_payload_messages(prompt: dict) -> list:
    """
    Converts a prompt dictionary into a structured JSON payload.

    Parameters
    ----------
    prompt : dict
        A dictionary containing 'system' and 'user' messages.

    Returns
    -------
    list
        A list of dictionaries formatted as chat messages.
    """
    logger.debug('prompt: {}'.format(prompt))
    if not isinstance(prompt, dict) or "system" not in prompt or "user" not in prompt:
        raise ValueError("Input must be a dictionary containing 'system' and 'user' keys.")

    return [
        {"role": "system", "content": prompt["system"]},
        {"role": "user", "content": prompt["user"]}
    ]