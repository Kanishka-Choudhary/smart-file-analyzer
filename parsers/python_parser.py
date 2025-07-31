# parsers/python_parser.py

import ast

def extract_structure_from_code(code):
    tree = ast.parse(code)
    result = {
        "classes": [],
        "functions": [],
    }

    for node in ast.walk(tree):
        # Class Definitions
        if isinstance(node, ast.ClassDef):
            class_info = {
                "name": node.name,
                "methods": [],
                "base_classes": [base.id for base in node.bases if isinstance(base, ast.Name)],
                "lineno": node.lineno
            }

            for body_item in node.body:
                if isinstance(body_item, ast.FunctionDef):
                    method_info = {
                        "name": body_item.name,
                        "params": [arg.arg for arg in body_item.args.args],
                        "lineno": body_item.lineno
                    }
                    class_info["methods"].append(method_info)

            result["classes"].append(class_info)

        # Standalone Functions
        elif isinstance(node, ast.FunctionDef) and isinstance(getattr(node, 'parent', None), ast.Module):
            func_info = {
                "name": node.name,
                "params": [arg.arg for arg in node.args.args],
                "lineno": node.lineno
            }
            result["functions"].append(func_info)

    return result


# 👇 Needed to walk the AST properly with parent info
def attach_parents(tree):
    for node in ast.walk(tree):
        for child in ast.iter_child_nodes(node):
            child.parent = node
    return tree


def analyze_python_code(code):
    tree = ast.parse(code)
    attach_parents(tree)
    return extract_structure_from_code(code)
