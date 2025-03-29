from datetime import datetime

from punito.tests_generator.generator_utils import get_test_example
from punito.utils import read_file, extract_class_name, find_project_root
from punito.processing import get_chunked_code
from pathlib import Path

def main() -> None:
    """
    Script for testing test generation for a specific class.
    It executes the full test generation pipeline for each chunk of code.
    """

    class_path = Path(
        r"C:\moeve_IDE\moeve-ide\workspaces\main\moeve-vvst\moeve-enst-dlg\src\main"
        r"\java\de\itzbund\moeve\enst\taxation\taxation\dlg\af200\controller"
        r"\Af200EnergyBasicdataGeneralPanelControllerBean.java"
    )

    example_code = get_test_example("PanelControllerExampleMockitoTest.java")

    save_path = Path(__file__).parent / "debug" / "latest" / "generate_tests_for_class" / "class_tests.txt"
    # TODO implement

if __name__ == "__main__":
    main()
