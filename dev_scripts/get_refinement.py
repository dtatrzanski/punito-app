from datetime import datetime
from punito import generate_refined_tests
from punito.utils import read_file, extract_class_name, find_project_root
from punito.utils import write_to_file
from punito.processing import get_chunked_code
from pathlib import Path


def main() -> None:
    class_path = Path(
        r"C:\moeve_IDE\moeve-ide\workspaces\main\moeve-vvst\moeve-enst-dlg\src\main"
        r"\java\de\itzbund\moeve\enst\taxation\taxation\dlg\af200\controller"
        r"\Af200EnergyBasicdataGeneralPanelControllerBean.java"
    )

    common_path = find_project_root() / 'generated_tests' / '0.1.0' / '2025-03-25T08-37-02.791307' / 'Af200EnergyBasicdataGeneralPanelControllerBean' / 'tests_per_public_function' / 'initializePanel' / 'hideElementsfrom119to137'
    tests_path = common_path / 'initial_onChangeOfTaxDeclarationImmediately.java'
    review_path = common_path / 'review_onChangeOfTaxDeclarationImmediately.txt'

    execution_function_name = "initializePanel"
    tested_function_name = "hideElementsfrom119to137"

    class_code = read_file(class_path)

    chunked_code = get_chunked_code(class_code)

    function_code = chunked_code[execution_function_name][tested_function_name]

    write_to_file(function_code,
                  Path(__file__).parent / "debug" / "generate_tests_for_function" / "extracted_function.txt")

    date_time = datetime.now().isoformat().replace(":", "-")

    tests = read_file(tests_path)

    review = read_file(review_path)

    refinement = generate_refined_tests(function_code, extract_class_name(class_path), execution_function_name, tested_function_name,
                           date_time, review, tests)

    write_to_file(refinement,
                  Path(__file__).parent / "debug" / "get_refinement" / "refined_tests.txt")


if __name__ == "__main__":
    main()
