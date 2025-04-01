import re
import javalang
from typing import List

def collect_class_tests(chunks: List[str], class_name: str) -> str:
    imports_set = set()
    test_methods = []
    util_methods = []
    mock_fields = {}
    class_annotations = []

    class_extends = None

    for i, chunk in enumerate(chunks):
        chunk = re.sub(r'^```java\n|```$', '', chunk.strip())
        lines = chunk.splitlines()
        tree = javalang.parse.parse(chunk)

        # Collect imports
        for imp in tree.imports:
            imports_set.add(f'import {imp.path};')

        # Extract class info and annotations from first chunk only
        if i == 0:
            class_decl = next(
                (node for _, node in tree.filter(javalang.tree.ClassDeclaration)), None
            )
            if class_decl:
                # Get extends
                if class_decl.extends:
                    class_extends = class_decl.extends.name

                # Get class annotations
                for annotation in class_decl.annotations:
                    ann_str = "@" + annotation.name
                    if annotation.element:
                        # Handle annotations with parameters like @RunWith(SomeClass.class)
                        element_str = chunk[annotation.position.offset:].split('\n', 1)[0].strip()
                        ann_str = element_str
                    class_annotations.append(ann_str)

        # Collect @Mock and @InjectMocks fields
        for _, class_node in tree.filter(javalang.tree.ClassDeclaration):
            for field in class_node.fields:
                annotations = {anno.name for anno in field.annotations}
                if 'Mock' in annotations or 'InjectMocks' in annotations:
                    line_num = field.position.line - 1

                    # Look upward to include annotations
                    annotation_lines = []
                    i = line_num - 1
                    while i >= 0 and lines[i].strip().startswith('@'):
                        annotation_lines.insert(0, lines[i].strip())
                        i -= 1

                    field_line = lines[line_num].strip()
                    full_field = '\n'.join(annotation_lines + [field_line])

                    for declarator in field.declarators:
                        mock_fields[declarator.name] = full_field

            # Extract methods
            for method in class_node.methods:
                start_line = method.position.line - 1
                brace_count = 0
                end_line = start_line

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

    imports_section = '\n'.join(sorted(imports_set))
    class_annotations_section = '\n'.join(class_annotations)
    mock_fields_section = '\n'.join(mock_fields.values())
    test_methods_section = '\n\n'.join(test_methods)
    util_methods_section = '\n\n'.join(util_methods)
    extends_clause = f" extends {class_extends}" if class_extends else ""

    merged_class = (
        f"{imports_section}\n\n"
        f"{class_annotations_section}\n"
        f"public class {class_name}{extends_clause} {{\n\n"
        f"{mock_fields_section}\n\n"
        f"{test_methods_section}\n\n"
        f"{util_methods_section}\n"
        f"}}"
    )

    return merged_class
