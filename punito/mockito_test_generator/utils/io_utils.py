from loguru import logger

def read_class_file(class_path: str) -> str:
    """
    Reads a Java class file from the given path.

    Parameters
    ----------
    class_path : str
        Path to the Java class file.

    Returns
    -------
    str
        The content of the Java class file, or an empty string in case of an error.
    """

    try:
        logger.info(f"Reading class file: {class_path}")
        with open(class_path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        logger.error(f"Error reading class file: {e}")
        return ""