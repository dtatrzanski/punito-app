import json
from datetime import datetime
from pathlib import Path

from punito import TestsGenerator
from punito.utils import (
    read_file,
    extract_class_name,
    find_project_root,
    write_to_file,
)
from punito.processing import get_chunked_code
from utils import save_chunks


def main() -> None:
    """
    Development script for testing test generation for a specific function.
    """

    class_path = Path(
        r"C:\moeve_IDE\moeve-ide\workspaces\main\moeve-vvst\moeve-enst-dlg\src\main"
        r"\java\de\itzbund\moeve\enst\taxation\taxation\dlg\af200\controller"
        r"\Af200EnergyBasicdataGeneralPanelControllerBean.java"
    )

    example_path = (
        find_project_root()
        / "punito"
        / "resources"
        / "test_examples"
        / "PanelControllerExampleMockitoTest.java"
    )

    execution_function_name = "initializePanel"
    tested_function_name = "hideElementsfrom119to137"

    class_code = read_file(class_path)
    example_code = read_file(example_path)

    chunked_code = get_chunked_code(class_code)

    save_chunks(
        json.dumps(chunked_code),
        Path(__file__).parent / "debug" / "get_chunked_code" / "chunked_code.txt",
    )

    function_code = chunked_code[execution_function_name][tested_function_name]

    write_to_file(
        function_code,
        Path(__file__).parent
        / "debug"
        / "generate_tests_for_function"
        / "extracted_function.txt",
    )

    date_time = datetime.now().isoformat().replace(":", "-")
    class_name = extract_class_name(class_path)

    generator = TestsGenerator(class_name=class_name, date_time=date_time)

    final_tests = generator.generate_tests_for_function(
        function_code=function_code,
        exe_fn_name=execution_function_name,
        tst_fn_name=tested_function_name,
        example_code=example_code,
    )

    write_to_file(
        final_tests,
        Path(__file__).parent
        / "debug"
        / "generate_tests_for_function"
        / f"{tested_function_name}_final.java",
    )


if __name__ == "__main__":
    main()
