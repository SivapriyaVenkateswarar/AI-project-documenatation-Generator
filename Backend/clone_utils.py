from git import Repo
import os
import shutil
import ast
import re
import javalang
from tree_sitter_languages import get_parser

# --------------------------------------------
# Global Configurations
# --------------------------------------------
EXCLUDE_FOLDERS = {".git", "__pycache__", "node_modules", ".vscode", "venv"}
LANGUAGE_EXT_MAP = {
    "c": "c",
    "cpp": "cpp",
    "cc": "cpp",
    "h": "cpp",  
    "rb": "ruby",
    "go": "go",
    "ts": "typescript",
    "php": "php",
    "html": "html",
    "css": "css",
}

# --------------------------------------------
# CLONE FUNCTION
# --------------------------------------------
def clone_and_analyze_repo(git_url: str, clone_dir: str = r"P:\AI_Documentation\example\cloned_repos"):
    """
    Clones the given repository and performs full multi-language code analysis.
    Returns the structured analysis tree.
    """

    # Step 1: Clean old repo
    if os.path.exists(clone_dir):
        print(f"Deleting existing directory {clone_dir}")
        shutil.rmtree(clone_dir, ignore_errors=True)

    # Step 2: Clone repository
    try:
        Repo.clone_from(git_url, clone_dir)
        print(f"Cloned {git_url} into {clone_dir}")
    except Exception as e:
        raise Exception(f"Failed to clone repository: {e}")

    # Step 3: Build code analysis tree
    analysis_tree = build_code_analysis_tree(clone_dir)
    print("Repository analysis complete.")
    return analysis_tree


# --------------------------------------------
# LANGUAGE-SPECIFIC ANALYZERS
# --------------------------------------------
def analyze_python_code(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            source = f.read()
        tree = ast.parse(source)

        class_count = sum(isinstance(n, ast.ClassDef) for n in ast.walk(tree))
        func_count = sum(isinstance(n, ast.FunctionDef) for n in ast.walk(tree))
        import_stmts = [n.names[0].name for n in ast.walk(tree) if isinstance(n, ast.Import)]
        import_stmts += [n.module for n in ast.walk(tree) if isinstance(n, ast.ImportFrom)]
        has_docstrings = ast.get_docstring(tree) is not None
        lines_of_code = len(source.splitlines())

        return {
            "language": "python",
            "lines_of_code": lines_of_code,
            "classes_count": class_count,
            "functions_count": func_count,
            "imports": import_stmts,
            "has_docstrings": has_docstrings,
            "uml_target": class_count > 0
        }
    except Exception as e:
        print(f"[!] Error analyzing Python file {file_path}: {e}")
        return None


def analyze_js_code(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            source = f.read()

        class_count = len(re.findall(r'\bclass\s+\w+', source))
        func_count = len(re.findall(r'\bfunction\b|\b=>\s*\(', source))
        import_stmts = re.findall(r'\bimport\s.+?from\s+[\'"].+?[\'"]', source)
        import_stmts += re.findall(r'\brequire\s*\(\s*[\'"].+?[\'"]\s*\)', source)
        has_docstrings = '/**' in source or '/*' in source
        lines_of_code = len(source.splitlines())

        return {
            "language": "javascript",
            "lines_of_code": lines_of_code,
            "classes_count": class_count,
            "functions_count": func_count,
            "imports": import_stmts,
            "has_docstrings": has_docstrings,
            "uml_target": class_count > 0
        }
    except Exception as e:
        print(f"[!] Error analyzing JS file {file_path}: {e}")
        return None


def analyze_java_code(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            source = f.read()
        tree = javalang.parse.parse(source)

        class_count = len([node for _, node in tree.filter(javalang.tree.ClassDeclaration)])
        method_count = len([node for _, node in tree.filter(javalang.tree.MethodDeclaration)])
        import_stmts = [imp.path for imp in tree.imports]
        has_docstrings = '/**' in source or '/*' in source
        lines_of_code = len(source.splitlines())

        return {
            "language": "java",
            "lines_of_code": lines_of_code,
            "classes_count": class_count,
            "functions_count": method_count,
            "imports": import_stmts,
            "has_docstrings": has_docstrings,
            "uml_target": class_count > 0
        }
    except Exception as e:
        print(f"[!] Error analyzing Java file {file_path}: {e}")
        return None


def analyze_tree_sitter_code(file_path, language_name):
    try:
        parser = get_parser(language_name)
        with open(file_path, "r", encoding="utf-8", errors="replace") as f:
            source = f.read()
        tree = parser.parse(source.encode())
        root = tree.root_node

        def walk_tree(node):
            return {
                "type": node.type,
                "start": node.start_point,
                "end": node.end_point,
                "children": [walk_tree(c) for c in node.children if c.is_named]
            }

        return {
            "language": language_name,
            "lines_of_code": len(source.splitlines()),
            "ast": walk_tree(root)
        }
    except Exception as e:
        print(f"[!] Error analyzing file {file_path}: {e}")
        return None


# --------------------------------------------
# DIRECTORY WALKER
# --------------------------------------------
def build_code_analysis_tree(path, root_path=None, depth=0):
    if root_path is None:
        root_path = path

    name = os.path.basename(path)
    rel_path = os.path.relpath(path, root_path).replace("\\", "/")

    # Directory
    if os.path.isdir(path):
        if name in EXCLUDE_FOLDERS:
            return None

        node = {"name": name, "path": rel_path, "type": "folder", "depth": depth, "children": []}

        try:
            for item in sorted(os.listdir(path)):
                full_path = os.path.join(path, item)
                child = build_code_analysis_tree(full_path, root_path, depth + 1)
                if child:
                    node["children"].append(child)
        except Exception as e:
            print(f"[!] Error reading directory {path}: {e}")

        return node

    # File
    else:
        _, ext = os.path.splitext(name)
        ext = ext.lstrip(".").lower()

        if ext == "py":
            analysis = analyze_python_code(path)
        elif ext == "js":
            analysis = analyze_js_code(path)
        elif ext == "java":
            analysis = analyze_java_code(path)
        else:
            language_name = LANGUAGE_EXT_MAP.get(ext)
            if language_name:
                analysis = analyze_tree_sitter_code(path, language_name)
            else:
                return None

        if analysis:
            return {"name": name, "path": rel_path, "type": "file", "depth": depth, **analysis}
        return None
