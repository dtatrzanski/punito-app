import javalang
from typing import List
import re


def collect_class_tests(chunks: List[str]) -> str:
    imports_set = set()
    test_methods = []
    util_methods = []

    first_class_name = None

    for i, chunk in enumerate(chunks):
        chunk = re.sub(r'^```java\n|```$', '', chunk.strip())
        tree = javalang.parse.parse(chunk)

        # Collect imports
        for imp in tree.imports:
            imports_set.add(f'import {imp.path};')

        # Collect class name from first chunk
        if i == 0:
            class_decl = next(
                (node for _, node in tree.filter(javalang.tree.ClassDeclaration)), None
            )
            if class_decl:
                first_class_name = class_decl.name

        # Extract methods
        lines = chunk.split('\n')
        for _, class_node in tree.filter(javalang.tree.ClassDeclaration):
            for method in class_node.methods:
                start_line = method.position.line - 1
                brace_count = 0
                end_line = start_line

                # Find method end by balancing braces
                for idx in range(start_line, len(lines)):
                    brace_count += lines[idx].count('{') - lines[idx].count('}')
                    if brace_count == 0 and idx != start_line:
                        end_line = idx
                        break

                method_lines = lines[start_line:end_line + 1]
                method_str = '\n'.join(method_lines)

                if method.modifiers and "private" in method.modifiers:
                    util_methods.append(method_str)
                else:
                    test_methods.append(method_str)

    # Construct merged class
    imports_section = '\n'.join(sorted(imports_set))

    test_methods_section = '\n\n'.join(test_methods)
    util_methods_section = '\n\n'.join(util_methods)

    merged_class = (
        f"{imports_section}\n\n"
        f"public class {first_class_name} {{\n\n"
        f"{test_methods_section}\n\n"
        f"{util_methods_section}\n"
        f"}}"
    )

    return merged_class