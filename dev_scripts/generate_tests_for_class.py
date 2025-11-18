from datetime import datetime
from punito import TestsGenerator
from pathlib import Path
from punito.utils import extract_class_name


def main() -> None:
    """
    Script for testing test generation for a specific class.
    It executes the full test generation pipeline for each chunk of code.
    """
    class_path = Path(
        r"C:\Projects\moeve\R3\devon-ide\workspaces\main\moeve-enst\moeve-enst-dlg\src\main\java\de\itzbund\moeve\enst\permission\application\dlg\af100\controller\OtherAdmissionsPanelControllerBean.java"
    )

    generator = TestsGenerator(extract_class_name(class_path), datetime.now().isoformat().replace(":", "-"))
    generator.generate_tests_for_class(class_path=class_path)


if __name__ == "__main__":
    main()
