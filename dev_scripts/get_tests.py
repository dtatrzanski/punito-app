import json
from datetime import datetime
from punito import generate_tests_for_function, generate_plan_for_function, generate_review_for_function, generate_refined_tests
from punito.utils import read_file, extract_class_name, find_project_root
from punito.utils import write_to_file
from punito.processing import get_chunked_code
from pathlib import Path
from utils import save_chunks

def main() -> None:

    class_path = Path(
        r"C:\moeve_IDE\moeve-ide\workspaces\main\moeve-vvst\moeve-enst-dlg\src\main"
        r"\java\de\itzbund\moeve\enst\taxation\taxation\dlg\af200\controller"
        r"\Af200EnergyBasicdataGeneralPanelControllerBean.java"
    )

    example_path = find_project_root() / "punito" / "resources" / "test_examples" / "PanelControllerExampleMockitoTest.java"

    execution_function_name = "initializePanel"
    tested_function_name = "hideElementsfrom119to137"

    class_code = read_file(class_path)
    example_code = read_file(example_path)

    chunked_code = get_chunked_code(class_code)

    save_chunks(json.dumps(chunked_code), Path(__file__).parent / "debug" / "get_chunked_code" / "chunked_code.txt")

    function_code = chunked_code[execution_function_name][tested_function_name]

    write_to_file(function_code, Path(__file__).parent / "debug" / "generate_tests_for_function" / "extracted_function.txt")

    date_time = datetime.now().isoformat().replace(":", "-")

    common_path = find_project_root() / 'generated_tests' / '0.1.0' / '2025-03-25T08-27-32.827598' / 'Af200EnergyBasicdataGeneralPanelControllerBean' / 'tests_per_public_function' / 'initializePanel' / 'hideElementsfrom119to137'
    plan_path = common_path / 'plan_hideElementsfrom119to137.txt'

    plan = read_file(plan_path)

    tests = generate_tests_for_function(function_code, extract_class_name(class_path), execution_function_name, tested_function_name, date_time, plan, example_code)

    write_to_file(tests,
                  Path(__file__).parent / "debug" / "get_tests" / "tests.txt")

if __name__ == "__main__":
    main()
