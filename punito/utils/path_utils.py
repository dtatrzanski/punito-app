from pathlib import Path

def find_project_root() -> Path:
    """
    Returns the path to root directory of the project.

    Returns
    -------
    Path
        Path to the root directory of the project.
    """

    return next(p for p in Path(__file__).resolve().parents if p.name == "punito_app")

def find_resources_path() -> Path:
    """
    Returns the path to the package resources.

    Returns
    -------
    Path
        Path to the package resources.
    """
    return find_project_root() / 'punito' / 'resources'

def extract_class_name(file_path: str) -> str:
    """
        Extracts the Java class name from a given file path.

        Parameters
        ----------
        file_path : str
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

    path = Path(file_path)

    if path.suffix != ".java":
        raise ValueError(f"Invalid file type: {path.suffix}. Expected a .java file.")

    # Extract the class name (filename without extension)
    return path.stem
