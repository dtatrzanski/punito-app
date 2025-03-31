from punito.utils import extract_class_name
from punito.tests_generator.generator_utils import get_test_example
from dev_utils import generate_and_save, find_latest_generation_chunk
from pathlib import Path


def main() -> None:
    """
    Script for testing test generation for specific function.
    It generates initial tests (before review and refinement).
    """

    class_path = Path(
        r"C:\moeve_IDE\moeve-ide\workspaces\main\moeve-vvst\moeve-enst-dlg\src\main"
        r"\java\de\itzbund\moeve\enst\taxation\taxation\dlg\af200\controller"
        r"\Af200EnergyBasicdataGeneralPanelControllerBean.java"
    )
    execution_function_name = "basicdataStateAidAStateAidSelfdeclarationWillBeSubmittOnChange"
    tested_function_name = "basicdataStateAidAStateAidSelfdeclarationWillBeSubmittOnChange"
    save_path = Path(__file__).parent / "debug" / "latest" / "generate_tests" / "tests.txt"
    plan = find_latest_generation_chunk(extract_class_name(class_path), execution_function_name,
                                        f"plan_{tested_function_name}.txt")

    @generate_and_save(class_path, execution_function_name, tested_function_name, save_path)
    def run_generation(generator, function_code):
        return generator.generate_tests(
            function_code=function_code,
            exe_fn_name=execution_function_name,
            tst_fn_name=tested_function_name,
            tests_plan=plan,
            example_code=get_test_example("PanelControllerExampleMockitoTest.java")
        )

    run_generation()


if __name__ == "__main__":
    main()
