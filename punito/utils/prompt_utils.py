from .path_utils import find_resources_path
from .io_utils import read_yaml
from loguru import logger

def create_prompt_from_yaml(file_name: str, placeholders: dict) -> dict:
    """
    Reads a JSON template file, replaces placeholders, and returns the formatted JSON.

    Parameters
    ----------
    file_name : str
        Name of the JSON file located in the resources directory.
    placeholders : dict
        Dictionary containing placeholder values to replace.

    Returns
    -------
    dict
        The JSON data with placeholders replaced.
    """

    data = read_yaml(find_resources_path() / 'prompts' / (file_name + '.yaml'))
    logger.debug(data)
    if "user" in data:
        try:
            data["user"] = data["user"].format(**placeholders)
        except KeyError as e:
            logger.error(f"Missing placeholder: {e}")
            return {}

    return data

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