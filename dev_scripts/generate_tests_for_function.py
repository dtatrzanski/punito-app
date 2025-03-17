from datetime import datetime

from punito import generate_tests_for_function
from punito.utils import read_file, extract_class_name, write_to_file, find_project_root
from punito.utils import get_package_version, get_default_settings
from punito.processing import get_function_with_individual_dependencies, get_all_methods, parse_java_class
from loguru import logger
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

    class_path = (
        r"C:\moeve_IDE\moeve-ide\workspaces\main\moeve-vvst\moeve-enst-dlg\src\main"
        r"\java\de\itzbund\moeve\enst\taxation\taxation\dlg\af200\controller"
        r"\Af200EnergyBasicdataGeneralPanelControllerBean.java"
    )
    function_name = "onChangeMonthPeriod"

    class_code = read_file(class_path)
    parsed_code = parse_java_class(class_code)

    function_code = get_function_with_individual_dependencies(class_code, function_name, get_all_methods(parsed_code))

    def save_json_to_txt(json_data, file_name):
        script_dir = os.path.dirname(os.path.abspath(__file__))  # Get script directory
        file_path = os.path.join(script_dir, file_name)  # Create full file path

        with open(file_path, 'w', encoding='utf-8') as file:
            parsed_data = json.loads(json_data)
            for key, value in parsed_data.items():
                file.write(f"{key}:\n{value}\n\n")

        print(f"JSON data has been stored in {file_path}")

    # Example JSON string (replace with your actual JSON input)
    json_string = json.dumps(function_code)

    # Specify the output file name
    output_file = "output.txt"

    # Save JSON data to txt
    save_json_to_txt(json_string, output_file)

    generate_tests_for_function(function_code['onChangeMonthYearCommon'], extract_class_name(class_path), function_name)

if __name__ == "__main__":
    main()
