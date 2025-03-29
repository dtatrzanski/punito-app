from dev_utils import generate_and_save
from pathlib import Path


def main() -> None:
    """
    Script for testing plan generation for specific function.
    """

    class_path = Path(
        r"C:\moeve_IDE\moeve-ide\workspaces\main\moeve-vvst\moeve-enst-dlg\src\main"
        r"\java\de\itzbund\moeve\enst\taxation\taxation\dlg\af200\controller"
        r"\Af200EnergyBasicdataGeneralPanelControllerBean.java"
    )
    execution_function_name = "initializePanel"
    tested_function_name = "initializePanel"
    save_path = Path(__file__).parent / "debug" / "latest" / "generate_plan" / "tests_plan.txt"

    @generate_and_save(class_path, execution_function_name, tested_function_name, save_path)
    def run_generation(generator, function_code):
        return generator.generate_plan(
            function_code=function_code,
            exe_fn_name=execution_function_name,
            tst_fn_name=tested_function_name,
        )

    run_generation()


if __name__ == "__main__":
    main()
