from punito import generate_tests_for_function
from punito.utils import read_file, extract_class_name
from punito.utils import get_package_version, get_default_settings

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
    generate_tests_for_function(class_code, extract_class_name(class_path), function_name)

if __name__ == "__main__":
    main()
