from punito.utils import  extract_class_name
from punito.utils import write_to_file
from pathlib import Path
from dev_utils import find_latest_generation, generate_and_save


def main() -> None:
    """
    Script for testing the review step.
    """

    class_path = Path(
        r"C:\moeve_IDE\moeve-ide\workspaces\main\moeve-vvst\moeve-enst-dlg\src\main"
        r"\java\de\itzbund\moeve\enst\taxation\taxation\dlg\af200\controller"
        r"\Af200EnergyBasicdataGeneralPanelControllerBean.java"
    )

    execution_function_name = "initializePanel"
    tested_function_name = "initializePanel"

    tests = find_latest_generation(extract_class_name(class_path), execution_function_name,
                           tested_function_name, f"initial_{tested_function_name}.java")

    save_path = Path(__file__).parent / "debug" / "latest" / "generate_review" / "tests_review.txt"

    @generate_and_save(class_path, execution_function_name, tested_function_name, save_path)
    def run_generation(generator, function_code):
        return generator.generate_review(
            function_code=function_code,
            exe_fn_name=execution_function_name,
            tst_fn_name=tested_function_name,
            test_code=tests,
        )

    run_generation()

if __name__ == "__main__":
    main()
