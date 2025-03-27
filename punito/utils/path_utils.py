from pathlib import Path
from .config_utils import get_default_settings, get_package_name

def find_project_root() -> Path:
    """
    Returns the path to root directory of the project.

    Returns
    -------
    Path
        Path to the root directory of the project.
    """
    root = get_default_settings()["ROOT_DIR"]
    try:
        return next(p for p in Path(__file__).resolve().parents if p.name == root)
    except StopIteration:
        raise RuntimeError(f"Project root folder '{root}' not found in parent paths.")

def find_resources_path() -> Path:
    """
    Returns the path to the package resources.

    Returns
    -------
    Path
        Path to the package resources.
    """
    return find_project_root() / get_package_name() / 'resources'

def extract_class_name(path: Path) -> str:
    """
    Extracts the Java class name from a given file path.

    Parameters
    ----------
    path : Path
        The path to the Java file.

    Returns
    -------
    str
        The class name extracted from the file name.

    Raises
    ------
    ValueError
        If the file is not a `.java` file.
    """

    if path.suffix != ".java":
        raise ValueError(f"Invalid file type: {path.suffix}. Expected a .java file.")

    # Extract the class name (filename without extension)
    return path.stem
