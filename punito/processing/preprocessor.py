import javalang
import re
from typing import Set, Dict
from javalang.tree import CompilationUnit, MethodDeclaration, MethodInvocation, FieldDeclaration, ClassDeclaration


def parse_java_class(class_code: str) -> CompilationUnit:
    """
    Parses Java source code into an abstract syntax tree (AST).

    Parameters
    ----------
    class_code : str
        The Java source code as a string.

    Returns
    -------
    CompilationUnit
        The root node of the Java AST.
    """
    return javalang.parse.parse(class_code)


def get_class_definition(class_code: str) -> str:
    """
    Extracts the full class definition, including annotations, from the provided Java source code.

    Parameters
    ----------
    class_code : str
        The source code of the class as a string.

    Returns
    -------
    str
        The class definition block as a string. Includes annotations and extends/implements clauses.
    """
    pattern = r"((?:@\w+\s*)*)\b(public\s+class\s+\w+\s*(?:extends\s+[^{]+)?(?:\s+implements\s+[^{]+)?)\s*\{"
    match = re.search(pattern, class_code, re.MULTILINE)
    return (match.group(1) + match.group(2) + " {").strip() if match else ""


def get_class_fields(class_code: str) -> str:
    """
    Extracts field declarations from the provided Java source code while preserving complex initializations.

    Parameters
    ----------
    class_code : str
        The source code of the class as a string.

    Returns
    -------
    str
        A string containing all field declarations, formatted correctly with initial values.
    """
    pattern = r"(?P<modifiers>(?:\b(private|protected|public|static|final)\b\s*)+)\s*(?P<type>[\w<>,\s]+)\s+(?P<name>\w+)\s*(?P<init>=\s*[^;]+)?;"
    matches = re.finditer(pattern, class_code, re.MULTILINE)

    fields = []
    for match in matches:
        field_declaration = f"{match.group('modifiers').strip()} {match.group('type').strip()} {match.group('name').strip()}"
        if match.group('init'):
            field_declaration += f" {match.group('init').strip()}"
        field_declaration += ";"
        fields.append(field_declaration)

    return "\n".join(fields)


def get_all_methods(tree: CompilationUnit) -> Dict[str, MethodDeclaration]:
    """
    Retrieves all method declarations from a Java AST.

    Parameters
    ----------
    tree : CompilationUnit
        The root node of the Java AST.

    Returns
    -------
    Dict[str, MethodDeclaration]
        A dictionary mapping method names to their corresponding AST nodes.
    """
    methods = {}
    for _, node in tree.filter(MethodDeclaration):
        if node.body is None:
            continue
        methods[node.name] = node
    return methods


def get_method_calls(method_name: str, all_methods) -> Set[str]:
    """
    Identifies all method calls within a given method declaration.

    Parameters
    ----------
    method_name : str
        The name of AST node representing the method.
    all_methods : Dict[str, MethodDeclaration]
        A dictionary of all available methods.

    Returns
    -------
    Set[str]
        A set of names of methods invoked within the given method.
    """

    method = all_methods[method_name]
    method_names = all_methods.keys()
    calls = set()
    for _, node in method.filter(MethodInvocation):
        member = node.member
        if member in method_names:
            calls.add(node.member)
    return calls


def extract_method_code(class_code: str, method: MethodDeclaration) -> str:
    """
    Extracts the source code for a specific method from Java source code.

    Parameters
    ----------
    class_code : str
        The original Java source code.
    method : MethodDeclaration
        The AST node of the method to extract.

    Returns
    -------
    str
        The source code of the specified method.
    """
    lines = class_code.splitlines()
    start_pos = method.position.line - 1

    bracket_count = 0
    method_started = False
    method_code = []

    for line in lines[start_pos:]:
        method_code.append(line)
        bracket_count += line.count("{") - line.count("}")

        if '{' in line:
            method_started = True

        if method_started and bracket_count == 0:
            break

    return "\n".join(method_code)


def extract_imports(class_code: str) -> str:
    """
    Extracts all import statements from Java source code.

    Parameters
    ----------
    class_code : str
        The Java source code as a string.

    Returns
    -------
    str
        All import statements concatenated into a single string.
    """
    imports = []
    lines = class_code.splitlines()

    for line in lines:
        if line.strip().startswith("import "):
            imports.append(line.strip())

    return "\n".join(imports)


def get_dependencies(method_name: str, all_methods: Dict[str, MethodDeclaration], deps: Set[str]):
    """
    Recursively collects all methods that a given method depends on.

    Parameters
    ----------
    method_name : str
        The name of the method whose dependencies to collect.
    all_methods : Dict[str, MethodDeclaration]
        A dictionary of all available methods.
    deps : Set[str]
        A set to store collected dependencies.

    Returns
    -------
    None
    """
    if method_name not in all_methods or method_name in deps:
        return
    deps.add(method_name)

    for call in get_method_calls(method_name, all_methods):
        get_dependencies(call, all_methods, deps)


def get_function_with_individual_dependencies(class_code: str, target_method_name: str,
                                              all_methods: Dict[str, MethodDeclaration]) -> Dict[str, str]:
    """
    Generates separate code blocks for each direct dependency of a target method, including imports,
    the target method, and nested dependencies.

    Parameters
    ----------
    class_code : str
        The Java source code.
    target_method_name : str
        The name of the target method.
    all_methods : Dict[str, MethodDeclaration]
        A dictionary mapping method names to their corresponding AST nodes.
    Returns
    -------
    Dict[str, str]
        A dictionary where each key is a direct dependency method name, and each value is
        the source code block containing the dependency, its nested dependencies, imports,
        and the target method.
    """
    imports = extract_imports(class_code)
    class_definition = get_class_definition(class_code)
    class_fields = get_class_fields(class_code)
    target_calls = get_method_calls(target_method_name, all_methods)

    dependency_blocks = {}
    # TODO skip public dependencies -> they will be tested later separately
    for dep in target_calls:
        collected_methods = set()
        get_dependencies(dep, all_methods, collected_methods)

        methods_code = [extract_method_code(class_code, all_methods[method])
                        for method in collected_methods]

        target_method_code = extract_method_code(class_code, all_methods[target_method_name])

        full_code = f"{imports}\n\n{class_definition}\n{class_fields}\n\n{target_method_code}\n\n" + "\n\n".join(
            methods_code)
        dependency_blocks[dep] = full_code

    return dependency_blocks


def get_chunked_code(class_code: str) -> Dict[str, Dict[str, str]]:
    tree = parse_java_class(class_code)
    all_methods = get_all_methods(tree)

    public_methods = [
        method_name for method_name, method in all_methods.items() if "public" in method.modifiers
    ]

    return {method: get_function_with_individual_dependencies(class_code, method, all_methods)
            for method in public_methods}
