from dynaconf import Dynaconf
from pathlib import Path
from .path_utils import find_project_root

def get_config(path: Path) -> Dynaconf:
    return Dynaconf(settings_files=[path])

def get_default_settings() -> Dynaconf:
    """
    Retrieve the default settings from the `settings.toml` file.

    Returns
    -------
    Dynaconf
        The default configuration settings loaded from the `DEFAULT` section of `settings.toml`.

    Raises
    ------
    KeyError
        If the "DEFAULT" section is missing in the settings file.
    """

    return get_config(find_project_root() / "settings.toml")['DEFAULT']

def get_package_info() -> Dynaconf:
    return get_config(find_project_root() / "pyproject.toml")

def get_package_version() -> str:
    """
    Retrieve the package version from the `pyproject.toml` file.

    Returns
    -------
    str
        The package version specified in `tool.poetry.version` within `pyproject.toml`.

    Raises
    ------
    KeyError
        If the key "tool.poetry.version" is not found in the configuration.
    """

    return get_package_info().get("tool.poetry.version")