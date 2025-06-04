import json

def save_structure(structure, filename="repo_metadata.json"):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(structure, f, indent=2)
