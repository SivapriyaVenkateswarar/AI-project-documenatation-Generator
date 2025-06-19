import os
import json
import google.generativeai as genai
api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key="AIzaSyAV9KOb6L2eB-a7W-3imCSTGzVvc7ynViw")

model = genai.GenerativeModel("models/gemini-1.5-flash")

def read_file_content(base_path, rel_path):
    abs_path = os.path.join(base_path, rel_path)
    try:
        with open(abs_path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        print(f"[!] Could not read {rel_path}: {e}")
        return ""

def generate_prompt(file_node, content):
    truncated_code = content[:1500]  # Context control for Gemini input
    return f"""
You are a helpful code documentation assistant.

Please provide:
1. A high-level explanation of what the following Python file does.
2. Suggested docstrings for each function and class, if missing.

Filename: {file_node['name']}
Path: {file_node['path']}
Lines of Code: {file_node['lines_of_code']}
Imports: {file_node['imports']}
Classes: {file_node['classes_count']}
Functions: {file_node['functions_count']}
Has Docstrings: {file_node['has_docstrings']}

### Begin Code:
{truncated_code}
### End Code.
"""

def call_gemini(prompt):
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print(f"[!] Gemini generation failed: {e}")
        return ""

def walk_and_process(tree_node, base_path):
    if tree_node["type"] == "file" and tree_node["name"].endswith(".py") and not tree_node.get("summary_generated", False):
        content = read_file_content(base_path, tree_node["path"])
        if content.strip():
            print(f"[+] Generating summary for: {tree_node['path']}")
            prompt = generate_prompt(tree_node, content)
            summary = call_gemini(prompt)
            print(summary)
            print("=" * 80)
    elif tree_node["type"] == "folder":
        for child in tree_node.get("children", []):
            walk_and_process(child, base_path) 

BASE_REPO_PATH = r"P:\AI_Documentation\github_repo\cloned_repos"
INPUT_TREE_JSON = r"P:\AI_Documentation\code_analysis.json"

with open(INPUT_TREE_JSON, "r", encoding="utf-8") as f:
    tree = json.load(f)
walk_and_process(tree, BASE_REPO_PATH)
