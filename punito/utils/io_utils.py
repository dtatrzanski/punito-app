from loguru import logger
from pathlib import Path
import yaml

def _format_long_path(path: Path) -> str:
    """Convert a pathlib.Path object to a long Windows path (\\?\ prefix)."""
    return f"\\\\?\\{str(path.resolve())}"

def read_file(path: Path) -> str:
    """
    Reads a file from the given path.

    Parameters
    ----------
    path : Path
        Absolute path to the file.

    Returns
    -------
    str
        The content of the file, or an empty string in case of an error.
    """

    try:
        logger.debug(f"Reading file: {path}")
        long_file_path: str = _format_long_path(path)
        with open(long_file_path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        # TODO: cancel pipeline for chunk
        logger.error(f"Error reading file: {e}")
        return ""


def read_yaml(path: Path) -> dict:
    """
    Reads a YAML file from the given path and returns its content as a dictionary.

    Parameters
    ----------
    path : Path
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


def write_to_file(content: str, path: Path) -> None:
    """
    Writes the provided content to a specified file path.

    Parameters
    ----------
    content : str
        The text content to be written into the file.
    path : Path
        The destination path, including filename, where the content should be saved.

    Raises
    ------
    OSError
        If an error occurs during file writing or directory creation.
    """

    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        long_file_path: str = _format_long_path(path)
        with open(long_file_path, "w", encoding="utf-8") as f:
            f.write(content)
        logger.info(f"Content successfully written to {path}")
    except Exception as e:
        logger.error(f"Error writing file: {e}")
