import json
from pathlib import Path
from typing import List

from punito.utils import write_to_file
from loguru import logger
from punito.processing import get_chunked_code
from punito.utils import read_file, extract_class_name, find_project_root, get_package_version
from punito.tests_generator import TestsGenerator
from datetime import datetime
from functools import wraps


def _format_value(value, indent: int = 0) -> str:
    """
    Recursively formats a value (dict, list, or str) into a structured, indented string.
    """

    indentation = '    ' * indent
    if isinstance(value, dict):
        inner = "\n".join(f"{indentation}    {k}: {_format_value(v, indent + 1)}" for k, v in value.items())
        return f"{{\n{inner}\n{indentation}}}"
    elif isinstance(value, list):
        inner = "\n".join(f"{indentation}    - {_format_value(item, indent + 1)}" for item in value)
        return f"[\n{inner}\n{indentation}]"
    elif isinstance(value, str) and ('\n' in value or value.strip().startswith(
            ('import', 'public', '@', 'private', 'protected', 'class', 'def'))):
        # Treat string as code
        code_lines = "\n".join(f"{indentation}    {line}" for line in value.strip().splitlines())
        return f"\n{indentation}'\n{code_lines}\n{indentation}'"
    else:
        return f"{value}"


def save_chunks(chunks: str, file_path: Path):
    """
    Saves chunks to a text file with improved formatting:
    - Nested objects are clearly indented.
    - Code snippets are properly formatted.
    """

    try:
        parsed_data = json.loads(chunks)
        content = "\n".join(f"{k}:\n{_format_value(v, 1)}\n" for k, v in parsed_data.items())
        write_to_file(content, file_path)
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON format: {e}")
    except IOError as e:
        logger.error(f"Error writing to file: {e}")


def _get_function_code_and_save_debug(class_path: Path, exe_fn_name: str, tst_fn_name: str) -> str:
    """
    Extracts function code from a chunked code structure and saves debug files.
    """
    common_path = find_project_root() / 'dev_scripts' / "debug"

    chunked_code = get_chunked_code(read_file(class_path))
    save_chunks(json.dumps(chunked_code), common_path / "latest" / "chunked_code" / "chunked_code.txt")

    function_code = chunked_code[exe_fn_name][tst_fn_name]
    write_to_file(function_code, common_path / "latest" / "chunk.txt")

    return function_code


def generate_and_save(class_path: Path,
                      execution_function_name: str,
                      tested_function_name: str,
                      save_path: Path):
    """
    Decorator to generate and save content for a specified function.

    Parameters
    ----------
    class_path : Path
        Path to the Python file containing the class.
    execution_function_name : str
        Name of the function used to execute the test.
    tested_function_name : str
        Name of the function under test.
    save_path : Path
        Path to save the generated content.

    Returns
    -------
    Callable
        Decorator that wraps a content generation function.
    """

    def decorator(generate_func):
        @wraps(generate_func)
        def wrapper():
            function_code = _get_function_code_and_save_debug(
                class_path, execution_function_name, tested_function_name
            )
            generator = TestsGenerator(
                class_name=extract_class_name(class_path),
                date_time=datetime.now().isoformat().replace(":", "-")
            )
            result = generate_func(generator, function_code)
            write_to_file(result, save_path)
            return result

        return wrapper

    return decorator


def _get_generated_tests_path() -> Path:
    return find_project_root() / 'generated_tests' / get_package_version()


def find_latest_generation_chunk(
        class_name: str,
        execution_function_name: str,
        file_name: str,
) -> str:
    """
    Find latest generated file.

    Parameters
    ----------
    class_name: str
        Name of the java class.
    execution_function_name : str
        Name of the execution function.
    file_name : str
        Name of the generated file (with extension).

    Returns
    -------
    str
        Latest generated file.

    Raises
    ------
    FileNotFoundError
        If the base directory does not exist.
    ValueError
        If no matching generated file is found.
    """
    candidates = []
    base_dir = _get_generated_tests_path()
    exe_fn_path = Path(class_name) / 'tests_per_public_function' / execution_function_name

    if not base_dir.exists():
        raise FileNotFoundError(
            f"Directory '{base_dir}' does not exist. Preceding pipeline steps were not executed."
        )

    for child in base_dir.iterdir():
        if not child.is_dir():
            continue

        test_dir = child / exe_fn_path
        matches = list(test_dir.glob(f'{file_name}'))
        if matches:
            candidates.append((child.name, matches[0]))

    if not candidates:
        raise ValueError(
            f"No generation found for path: "
            f"{exe_fn_path}//{file_name}. "
            f"Preceding pipeline step was not executed."
        )

    return read_file(max(candidates, key=lambda x: x[0])[1])


def get_latest_artifact_path() -> Path:
    base_dir = _get_generated_tests_path()
    artifacts = [d for d in base_dir.iterdir() if d.is_dir()]

    return max(artifacts, key=lambda d: d.name)


def collect_chunks(base_dir: Path) -> List[str]:
    chunks = []
    for child in base_dir.iterdir():
        if child.is_dir():
            for java_file in child.rglob("*.java"):
                chunks.append(read_file(java_file))
    logger.debug("chunks: " + str(len(chunks)))
    return chunks
