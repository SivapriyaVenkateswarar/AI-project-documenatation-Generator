import os
import json

EXTENSION_LANG_MAP = {
    ".py": "Python",
    ".js": "JavaScript",
    ".java": "Java",
    ".cpp": "C++",
    ".c": "C",
    ".cs": "C#",
    ".rb": "Ruby",
    ".go": "Go",
    ".ts": "TypeScript",
    ".php": "PHP",
    ".html": "HTML",
    ".css": "CSS",
    "txt": "text"
}

def get_language(extension):
    return EXTENSION_LANG_MAP.get(extension.lower(), "Unknown")

EXCLUDE_FOLDERS = {".git", "node_modules", "__pycache__", "venv", "build", "dist"}

def build_tree_with_metadata(path, root_path=None, depth=0):
    if root_path is None:
        root_path = path

    name = os.path.basename(path)
    rel_path = os.path.relpath(path, root_path).replace("\\", "/")

    if os.path.isdir(path):
        if name in EXCLUDE_FOLDERS:
            # Skip excluded folders completely
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
                child_node = build_tree_with_metadata(full_path, root_path, depth + 1)
                if child_node is not None:
                    node["children"].append(child_node)
        except Exception as e:
            print(f"Error accessing {path}: {e}")
    else:
        extension = os.path.splitext(name)[1]
        node = {
            "name": name,
            "path": rel_path,
            "type": "file",
            "extension": extension,
            "depth": depth,
            "language": get_language(extension)
        }
    return node

tree = build_tree_with_metadata(r"P:\AI_Documentation\github_repo\cloned_repos")

# Save to a JSON file
with open("repo_metadata.json", "w", encoding="utf-8") as f:
    json.dump(tree, f, indent=2)
