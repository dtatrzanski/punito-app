from typing import Set, Dict
import javalang
from javalang.tree import CompilationUnit, MethodDeclaration

def parse_java_class(class_code: str) -> CompilationUnit:
    """
    Parses Java class code into an abstract syntax tree (AST).

    Parameters
    ----------
    class_code : str
        The Java source code

    Returns
    -------
    CompilationUnit
        The parsed Java AST representation of the class.
    """
    return javalang.parse.parse(class_code)

def get_all_methods(tree: CompilationUnit) -> Dict[str, MethodDeclaration]:
    """
    Extracts all method declarations from a parsed Java AST.

    Parameters
    ----------
    tree : CompilationUnit
        The parsed Java AST.

    Returns
    -------
    dict[str, MethodDeclaration]
        A dictionary where keys are method names and values are their corresponding AST nodes.
    """
    methods = {}
    for _, node in tree.filter(MethodDeclaration):
        methods[node.name] = node
    return methods

def get_method_calls(method: MethodDeclaration) -> Set[str]:
    """
    Extracts all method calls made within a given method.

    Parameters
    ----------
    method : MethodDeclaration
        The AST node representing the Java method.

    Returns
    -------
    set[str]
        A set of method names that are invoked within the given method.
    """
    calls = set()
    for _, node in method.filter(javalang.tree.MethodInvocation):
        calls.add(node.member)
    return calls

def extract_method_code(class_code: str, method: MethodDeclaration) -> str:
    """
    Extracts the source code of a specific method from the Java class code.

    Parameters
    ----------
    class_code : str
        The Java source code as a string.
    method : MethodDeclaration
        The AST node representing the method to extract.

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
    imports = []
    lines = class_code.splitlines()

    for line in lines:
        if line.strip().startswith("import "):
            imports.append(line.strip())

    return "\n".join(imports)

def get_function_with_dependencies(class_code: str, target_method_name: str) -> str:
    """
    Extracts a target method along with all its dependencies from Java source code.

    Parameters
    ----------
    class_code : str
        The Java source code as a string.
    target_method_name : str
        The name of the method to extract along with its dependencies.

    Returns
    -------
    str
        The source code of the target method and all methods it directly or indirectly depends on.
    """
    tree = parse_java_class(class_code)
    all_methods = get_all_methods(tree)
    collected_methods = {}

    def collect_dependencies(method_name: str):
        if method_name in collected_methods or method_name not in all_methods:
            return

        method_node = all_methods[method_name]
        collected_methods[method_name] = extract_method_code(class_code, method_node)

        dependencies = get_method_calls(method_node)
        for dep in dependencies:
            collect_dependencies(dep)

    collect_dependencies(target_method_name)
    imports = extract_imports(class_code)

    return f"{imports}\n\n" + "\n\n".join(collected_methods.values())