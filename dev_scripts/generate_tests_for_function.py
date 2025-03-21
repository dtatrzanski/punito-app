from datetime import datetime

from punito import generate_tests_for_function, generate_plan_for_function, generate_review_for_function, generate_refined_tests
from punito.utils import read_file, extract_class_name, find_project_root
from punito.utils import write_to_file
from punito.processing import get_chunked_code
from pathlib import Path
import json

def main() -> None:
    """
       Development script for testing test generation for a specific function.

       This function sets predefined values for `class_name` and `function_name`
       and calls `generate_tests_for_function` to generate test cases.

       Returns
       -------
       None

       Examples
       --------
       Run the script manually during development:

       ```sh
       python dev_scripts/generate_tests_for_function.py
       ```
       """

    class_path = Path(
        r"C:\moeve_IDE\moeve-ide\workspaces\main\moeve-vvst\moeve-enst-dlg\src\main"
        r"\java\de\itzbund\moeve\enst\taxation\taxation\dlg\af200\controller"
        r"\Af200EnergyBasicdataGeneralPanelControllerBean.java"
    )

    example_path = find_project_root() / "punito" / "resources" / "test_examples" / "PanelControllerExampleMockitoTest.java"

    execution_function_name = "onChangeOfTaxDeclarationImmediately"
    tested_function_name = "onChangeOfTaxDeclarationImmediately"

    class_code = read_file(class_path)
    example_code = read_file(example_path)

    chunked_code = get_chunked_code(class_code)

    function_code = chunked_code[execution_function_name][tested_function_name]

    write_to_file(function_code, Path(__file__).parent / "debug" / "generate_tests_for_function" / "extracted_function.txt")

    date_time = datetime.now().isoformat().replace(":", "-")

    plan = generate_plan_for_function(function_code, extract_class_name(class_path), execution_function_name, tested_function_name, date_time)

    tests = generate_tests_for_function(function_code, extract_class_name(class_path), execution_function_name, tested_function_name, date_time, plan, example_code)

    review = generate_review_for_function(function_code, extract_class_name(class_path), execution_function_name, tested_function_name, plan, tests, date_time)

    generate_refined_tests(function_code, extract_class_name(class_path), execution_function_name, tested_function_name, date_time, review, tests)

if __name__ == "__main__":
    main()
