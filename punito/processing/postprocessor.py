import re
import javalang
import hashlib
from collections import defaultdict
from typing import List, Dict

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
        # TODO handle parsing error - prompt to fix compilation for chunk
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

def extract_method_name(test_code: str) -> str:
    for line in test_code.splitlines():
        line = line.strip()
        if line.startswith("public void"):
            return line.split()[2].split("(")[0]
    return "<unknown>"

def extract_test_blocks(java_code: str) -> List[str]:
    tree = javalang.parse.parse(java_code)
    test_methods = []
    for _, node in tree:
        # Include methods with @Test annotation or whose name starts with 'should'
        if (isinstance(node, javalang.tree.MethodDeclaration) and
            (node.annotations or node.name.startswith("should"))):
            start_line = node.position.line - 1
            all_lines = java_code.splitlines()[start_line:]
            method_code, brace_count = [], 0
            for line in all_lines:
                method_code.append(line)
                brace_count += line.count('{')
                brace_count -= line.count('}')
                if brace_count <= 0:
                    break
            test_methods.append("\n".join(method_code))
    return test_methods

def extract_given_then_blocks(test_code: str):
    lines = test_code.splitlines()
    given_lines, then_lines = [], []
    current_section = None
    for line in lines:
        if '// given' in line:
            current_section = 'given'
            continue
        elif '// then' in line:
            current_section = 'then'
            continue
        elif '// when' in line:
            current_section = None
            continue

        if current_section == 'given':
            given_lines.append(line.strip())
        elif current_section == 'then':
            then_lines.append(line.strip())
    return "\n".join(given_lines), "\n".join(then_lines)

def normalize_statement(stmt: str) -> str:
    """
    Tokenizes using regex and keeps only tokens that are relevant for duplicate detection.
    This includes allowed keywords, class names (starting with uppercase), number literals, and boolean literals.
    """
    # Capture words, numbers, or quoted strings.
    tokens = re.findall(r'"[^"]*"|\b[A-Za-z_][A-Za-z0-9_]*\b|\d+(?:\.\d+)?', stmt)
    normalized = []
    allowed_tokens = {
        "new", "=", ".", "this", "assertThat", "isTrue", "isFalse",
        "isEqualTo", "isCloseTo", "within", "true", "false"
    }
    for tok in tokens:
        if tok in allowed_tokens:
            normalized.append(tok)
        elif tok[0].isupper():  # likely a class or constant
            normalized.append(tok)
        elif tok.isnumeric() or tok.replace(".", "", 1).isnumeric():
            normalized.append(tok)
        elif tok.startswith('"') and tok.endswith('"'):
            normalized.append(tok)
        # Skip variable names and others.
    return " ".join(normalized)

def normalize_block(block: str) -> str:
    # Normalize each line and sort to eliminate order issues.
    return "\n".join(sorted(normalize_statement(line) for line in block.splitlines() if line.strip()))

def hash_block(block: str) -> str:
    return hashlib.md5(block.encode()).hexdigest()

def find_duplicate_tests(test_class: str) -> List[Dict[str, List[str]]]:
    test_methods = extract_test_blocks(test_class)
    seen = {}
    duplicates = defaultdict(list)
    for test_code in test_methods:
        given, then = extract_given_then_blocks(test_code)
        given_norm = normalize_block(given)
        then_norm = normalize_block(then)
        key = (hash_block(given_norm), hash_block(then_norm))
        method_name = extract_method_name(test_code)
        if key in seen:
            duplicates[seen[key]].append(method_name)
        else:
            seen[key] = method_name
    return [{"test": test, "duplicates": dups} for test, dups in duplicates.items() if dups]


def remove_duplicate_tests(tests_code: str) -> str:
    duplicates = find_duplicate_tests(tests_code)
    print(duplicates)
    if not duplicates:
        return tests_code

    duplicate_method_names = {dup for group in duplicates for dup in group["duplicates"]}

    tree = javalang.parse.parse(tests_code)
    lines = tests_code.splitlines()
    method_ranges = []

    # Determine start and end lines of each method
    for _, node in tree:
        if isinstance(node, javalang.tree.MethodDeclaration):
            method_name = node.name
            if method_name in duplicate_method_names:
                start_line = node.position.line - 1
                # Extract method by counting braces
                method_code, brace_count = [], 0
                for idx in range(start_line, len(lines)):
                    method_code.append(lines[idx])
                    brace_count += lines[idx].count('{')
                    brace_count -= lines[idx].count('}')
                    if brace_count <= 0:
                        end_line = idx
                        method_ranges.append((start_line, end_line))
                        break

    # Remove duplicates in reverse order (to preserve indices)
    for start, end in sorted(method_ranges, reverse=True):
        del lines[start:end + 1]

    return "\n".join(lines)

