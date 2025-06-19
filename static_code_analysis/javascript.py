import re
import os
import ast
EXCLUDE_FOLDERS = {".git", "__pycache__", "node_modules", ".vscode", "venv"}

def analyze_js_code(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            source = f.read()

        class_count = len(re.findall(r'\bclass\s+\w+', source))
        func_count = len(re.findall(r'\bfunction\b|\b=>\s*\(', source))
        import_stmts = re.findall(r'\bimport\s.+?from\s+[\'"].+?[\'"]', source)
        import_stmts += re.findall(r'\brequire\s*\(\s*[\'"].+?[\'"]\s*\)', source)
        has_docstrings = '/**' in source or '/*' in source  # crude check
        lines_of_code = len(source.splitlines())

        return {
            "lines_of_code": lines_of_code,
            "classes_count": class_count,
            "functions_count": func_count,
            "imports": import_stmts,
            "has_docstrings": has_docstrings,
            "summary_generated": False,
            "uml_target": class_count > 0
        }
    except Exception as e:
        print(f"[!] Error analyzing JS file {file_path}: {e}")
        return None

def build_code_analysis_tree(path, root_path=None, depth=0):
    if root_path is None:
        root_path = path

    name = os.path.basename(path)
    rel_path = os.path.relpath(path, root_path).replace("\\", "/")

    if os.path.isdir(path):
        if name in EXCLUDE_FOLDERS:
            return None

        node = {
            "name": name,
            "path": rel_path,
            "type": "folder",
            "depth": depth,
            "children": []
        }

        try:
            for item in sorted(os.listdir(path)):
                full_path = os.path.join(path, item)
                child_node = build_code_analysis_tree(full_path, root_path, depth + 1)
                if child_node is not None:
                    node["children"].append(child_node)
        except Exception as e:
            print(f"[!] Error reading directory {path}: {e}")

        return node
    else:
        extension = os.path.splitext(name)[1].lower()

        if extension == ".js":
            analysis = analyze_js_code(path)
        else:
            return None

        if analysis:
            return {
                "name": name,
                "path": rel_path,
                "type": "file",
                "depth": depth,
                **analysis
            }
        return None

print(build_code_analysis_tree(r"P:\AI_Documentation\github_repo\cloned_repos"))
