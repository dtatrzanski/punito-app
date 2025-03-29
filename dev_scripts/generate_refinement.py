from dev_utils import generate_and_save, find_latest_generation
from punito.utils import extract_class_name
from pathlib import Path


def main() -> None:
    """
    Script for testing the refinement step.
    """

    class_path = Path(
        r"C:\moeve_IDE\moeve-ide\workspaces\main\moeve-vvst\moeve-enst-dlg\src\main"
        r"\java\de\itzbund\moeve\enst\taxation\taxation\dlg\af200\controller"
        r"\Af200EnergyBasicdataGeneralPanelControllerBean.java"
    )
    execution_function_name = "initializePanel"
    tested_function_name = "initializePanel"
    save_path = Path(__file__).parent / "debug" / "latest" / "generate_refinement" / "refined_tests.txt"

    tests = find_latest_generation(extract_class_name(class_path), execution_function_name,
                                       tested_function_name, f"initial_{tested_function_name}.java")
    review = find_latest_generation(extract_class_name(class_path), execution_function_name,
                                  tested_function_name, f"review_{tested_function_name}.txt")

    @generate_and_save(class_path, execution_function_name, tested_function_name, save_path)
    def run_generation(generator, _):
        return generator.generate_refined_tests(
            exe_fn_name=execution_function_name,
            tst_fn_name=tested_function_name,
            tests=tests,
            review_report=review
        )

    run_generation()


if __name__ == "__main__":
    main()
