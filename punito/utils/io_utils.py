from loguru import logger
from pathlib import Path
import yaml

def read_file(path: str) -> str:
    """
    Reads a file from the given path.

    Parameters
    ----------
    path : str
        Absolute path to the file.

    Returns
    -------
    str
        The content of the file, or an empty string in case of an error.
    """

    try:
        logger.info(f"Reading file: {path}")
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        logger.error(f"Error reading file: {e}")
        return ""

def read_yaml(path: Path) -> dict:
    """
    Reads a YAML file from the given path and returns its content as a dictionary.

    Parameters
    ----------
    path : str
        Absolute path to the YAML file.

    Returns
    -------
    dict
        The parsed YAML content, or an empty dictionary in case of an error.
    """
    try:
        logger.info(f"Reading YAML file: {path}")
        with open(path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    except (yaml.YAMLError, FileNotFoundError, IOError) as e:
        logger.error(f"Error reading YAML file: {e}")
        return {}

def write_to_file(content: str, file_path: Path) -> None:
    """
    Writes the provided content to a specified file path.

    Parameters
    ----------
    content : str
        The text content to be written into the file.
    file_path : str
        The destination path, including filename, where the content should be saved.

    Raises
    ------
    OSError
        If an error occurs during file writing or directory creation.
    """

    try:
        file_path.parent.mkdir(parents=True, exist_ok=True)
        with file_path.open("w", encoding="utf-8") as f:
            f.write(content)
        logger.info(f"Content successfully written to {file_path}")
    except Exception as e:
        logger.error(f"Error writing file: {e}")