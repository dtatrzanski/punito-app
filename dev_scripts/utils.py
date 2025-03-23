from pathlib import Path
from punito.utils import write_to_file
from loguru import logger
import json

def format_value(value, indent: int = 0) -> str:
    indentation = '    ' * indent
    if isinstance(value, dict):
        inner = "\n".join(f"{indentation}    {k}: {format_value(v, indent + 1)}" for k, v in value.items())
        return f"{{\n{inner}\n{indentation}}}"
    elif isinstance(value, list):
        inner = "\n".join(f"{indentation}    - {format_value(item, indent + 1)}" for item in value)
        return f"[\n{inner}\n{indentation}]"
    elif isinstance(value, str) and ('\n' in value or value.strip().startswith(('import', 'public', '@', 'private', 'protected', 'class', 'def'))):
        # Treat string as code
        code_lines = "\n".join(f"{indentation}    {line}" for line in value.strip().splitlines())
        return f"\n{indentation}'\n{code_lines}\n{indentation}'"
    else:
        return f"{value}"

def save_chunks(json_string: str, file_path: Path):
    """
    Save a JSON string to a text file with improved formatting:
    - Nested objects are clearly indented.
    - Code snippets are properly formatted.

    Parameters
    ----------
    json_string : str
        A JSON-formatted string to be saved.
    file_path : Path
        The path to the text file where the JSON data should be stored.

    Raises
    ------
    json.JSONDecodeError
        If `json_string` is not a valid JSON format.
    IOError
        If there is an issue writing to `file_path`.
    """
    try:
        parsed_data = json.loads(json_string)
        content = "\n".join(f"{k}:\n{format_value(v, 1)}\n" for k, v in parsed_data.items())
        write_to_file(content, file_path)
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON format: {e}")
    except IOError as e:
        logger.error(f"Error writing to file: {e}")