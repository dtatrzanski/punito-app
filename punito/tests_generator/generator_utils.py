from punito.utils import find_resources_path, read_file

def get_test_example(file_name: str) -> str:
    """Returns example of Mockito test."""

    return read_file(find_resources_path() / "test_examples" / file_name)

def create_log_for_runnable_invocation(prompt_name: str, tst_fn_name: str, exe_fn_name: str) -> str:
    return {
        "planner_prompt": f"Planning tests for function: {tst_fn_name}, triggered by {exe_fn_name}",
        "tester_prompt": f"Generating tests for function: {tst_fn_name}, triggered by {exe_fn_name}"
    }[prompt_name]
