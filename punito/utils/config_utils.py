from dynaconf import Dynaconf
from pathlib import Path

def _get_config(path: Path) -> Dynaconf:
    return Dynaconf(settings_files=[path])

def _get_root_path() -> Path:
    return Path(__file__).resolve().parents[2]

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

    return _get_config(_get_root_path() / "settings.toml")['DEFAULT']

def _get_package_info() -> Dynaconf:
    return _get_config(_get_root_path() / "pyproject.toml")

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

    return _get_package_info().get("tool.poetry.version")

def get_package_name() -> str:
    """
    Retrieve the package name from the `pyproject.toml` file.

    Returns
    -------
    str
        The package name specified in `tool.poetry.name` within `pyproject.toml`.

    Raises
    ------
    KeyError
        If the key "tool.poetry.name" is not found in the configuration.
    """
    return _get_package_info().get("tool.poetry.name")