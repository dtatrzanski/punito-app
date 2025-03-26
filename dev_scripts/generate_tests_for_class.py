from datetime import datetime
from punito import generate_tests_for_function, generate_plan_for_function, generate_review_for_function, generate_refined_tests
from punito.utils import read_file, extract_class_name, find_project_root
from punito.processing import get_chunked_code
from pathlib import Path

def main() -> None:

    class_path = Path(
        r"C:\moeve_IDE\moeve-ide\workspaces\main\moeve-vvst\moeve-enst-dlg\src\main"
        r"\java\de\itzbund\moeve\enst\taxation\taxation\dlg\af200\controller"
        r"\Af200EnergyBasicdataGeneralPanelControllerBean.java"
    )

    example_path = find_project_root() / "punito" / "resources" / "test_examples" / "PanelControllerExampleMockitoTest.java"

    class_code = read_file(class_path)
    example_code = read_file(example_path)

    chunked_code = get_chunked_code(class_code)

    date_time = datetime.now().isoformat().replace(":", "-")

    refined_tests = []
    for public_function, dependencies in chunked_code.items():
        for dep_name, dep_code in dependencies.items():
            plan = generate_plan_for_function(dep_code, extract_class_name(class_path), public_function,
                                              dep_name, date_time)

            tests = generate_tests_for_function(dep_code, extract_class_name(class_path), public_function,
                                                dep_name, date_time, plan, example_code)

            review = generate_review_for_function(dep_code, extract_class_name(class_path),
                                                  public_function, dep_name, tests, date_time)

            refined_tests.append(generate_refined_tests(dep_code, extract_class_name(class_path), public_function,
                                   dep_name, date_time, review, tests))


if __name__ == "__main__":
    main()
