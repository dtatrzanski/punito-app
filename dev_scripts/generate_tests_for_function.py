from datetime import datetime

from punito import generate_tests_for_function, generate_plan_for_function
from punito.utils import read_file, extract_class_name, write_to_file, find_project_root
from punito.utils import get_package_version, get_default_settings, save_json_to_txt
from punito.processing import get_function_with_individual_dependencies, get_all_methods, parse_java_class
from loguru import logger
from pathlib import Path
import json
import os

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

    execution_function_name = "onChangeMonthPeriodToCalendarYear"
    tested_function_name = "onChangeOfTaxPeriodIsCalendarYearToTrue"

    class_code = read_file(class_path)
    example_code = read_file(example_path)
    class_tree = parse_java_class(class_code)

    function_code = get_function_with_individual_dependencies(class_code, execution_function_name, get_all_methods(class_tree))

    save_json_to_txt(json.dumps(function_code), Path(__file__).parent / "debug" / "generate_tests_for_function" / "extracted_function.txt")

    date_time = datetime.now().isoformat().replace(":", "-")

    generate_plan_for_function(function_code[tested_function_name], extract_class_name(class_path), execution_function_name, tested_function_name, date_time)
    generate_tests_for_function(function_code[tested_function_name], extract_class_name(class_path), execution_function_name, tested_function_name, date_time, example_code)

if __name__ == "__main__":
    main()
