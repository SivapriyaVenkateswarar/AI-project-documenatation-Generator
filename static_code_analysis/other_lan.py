import os
from tree_sitter_languages import get_parser

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

def analyze_tree_sitter_code(file_path, language_name):
    try:
        parser = get_parser(language_name)
        with open(file_path, "r", encoding="utf-8", errors="replace") as f:
            source = f.read()
        tree = parser.parse(source.encode())
        root = tree.root_node

        def walk_tree(node):
            node_dict = {
                "type": node.type,
                "start": node.start_point,
                "end": node.end_point,
                "children": [walk_tree(child) for child in node.children if child.is_named]
            }
            return node_dict

        return {
            "lines_of_code": len(source.splitlines()),
            "ast": walk_tree(root),
            "summary_generated": False
        }
    except Exception as e:
        print(f"[!] Error analyzing file {file_path}: {e}")
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
        _, ext = os.path.splitext(name)
        ext = ext.lstrip(".").lower()  # clean extension
        language_name = LANGUAGE_EXT_MAP.get(ext)
        if not language_name:
            return None

        analysis = analyze_tree_sitter_code(path, language_name)
        if analysis:
            return {
                "name": name,
                "path": rel_path,
                "type": "file",
                "depth": depth,
                **analysis
            }
        return None

print(build_code_analysis_tree(r"P:\AI_Documentation\cloned_repos"))

