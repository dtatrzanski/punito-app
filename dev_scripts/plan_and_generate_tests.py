from pathlib import Path
from dev_utils import generate_and_save
from punito.tests_generator.generator_utils import get_test_example


def main() -> None:
    """
    Script for testing the full process of test generation for a specific function.
    It executes all steps in the pipeline.
    """

    class_path = Path(
        r"C:\moeve_IDE\moeve-ide\workspaces\main\moeve-vvst\moeve-enst-dlg\src\main"
        r"\java\de\itzbund\moeve\enst\taxation\taxation\dlg\af200\controller"
        r"\Af200EnergyBasicdataGeneralPanelControllerBean.java"
    )

    execution_function_name = "onChangeOfTaxDeclarationImmediately"
    tested_function_name = "onChangeOfTaxDeclarationImmediately"

    save_path = Path(__file__).parent / "debug" / "latest" / "generate_final_tests_for_function" / f"{tested_function_name}_final.java"

    @generate_and_save(class_path, execution_function_name, tested_function_name, save_path)
    def run_generation(generator, function_code):
        return generator.generate_tests_for_function(
            function_code=function_code,
            exe_fn_name=execution_function_name,
            tst_fn_name=tested_function_name,
            example_code=get_test_example("PanelControllerExampleMockitoTest.java")
        )

    run_generation()


if __name__ == "__main__":
    main()
