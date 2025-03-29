from datetime import datetime

from punito import TestsGenerator
from punito.tests_generator.generator_utils import get_test_example
from pathlib import Path

from punito.utils import extract_class_name


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

    generator = TestsGenerator(extract_class_name(class_path), datetime.now().isoformat().replace(":", "-") )
    generator.generate_tests_for_class(class_path=class_path)


if __name__ == "__main__":
    main()
