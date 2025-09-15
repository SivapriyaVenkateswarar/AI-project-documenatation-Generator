import os
import json
import google.generativeai as genai

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("models/gemini-1.5-flash")

def read_file_content(base_path, rel_path):
    abs_path = os.path.join(base_path, rel_path)
    try:
        with open(abs_path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        print(f"[!] Could not read {rel_path}: {e}")
        return ""

def generate_summary_prompt(file_node, content):
    truncated_code = content[:1500]
    return f"""
You are an expert AI Project Documentation Assistant.

Your task is to generate a concise, professional code summary intended for software engineers working on AI/ML or backend systems.

Please provide the following:
1. Purpose – What is the core objective of the code?
2. Key Components – Primary functions, classes, and their roles (no exhaustive docstrings).
3. Inputs and Outputs – Describe input data and outputs.
4. Dependencies – Mention major libraries used.
5. Use Case / Context – Where and how might this code be used?

Filename: {file_node['name']}
Path: {file_node['path']}
Lines of Code: {file_node['lines_of_code']}
Imports: {file_node['imports']}
Classes: {file_node['classes_count']}
Functions: {file_node['functions_count']}

### Begin Code:
{truncated_code}
### End Code.
"""

def generate_analysis_prompt(file_node, content):
    truncated_code = content[:1500]
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

def call_gemini(prompt, mode="summary"):
    try:
        print(f"[Gemini] Generating {mode}...")
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print(f"[!] Gemini generation failed: {e}")
        return f"Error generating {mode}: {e}"

def walk_and_process(tree_node, base_path):
    if tree_node["type"] == "file" and tree_node["name"].endswith(".py"):
        content = read_file_content(base_path, tree_node["path"])
        if content.strip():
            print(f"[+] Processing file: {tree_node['path']}")
            
            summary_prompt = generate_summary_prompt(tree_node, content)
            analysis_prompt = generate_analysis_prompt(tree_node, content)

            tree_node["summary"] = call_gemini(summary_prompt, "summary")
            tree_node["analysis"] = call_gemini(analysis_prompt, "analysis")
    elif tree_node["type"] == "folder":
        for child in tree_node.get("children", []):
            walk_and_process(child, base_path)

BASE_REPO_PATH = r"P:\AI_Documentation\github_repo\cloned_repos"
INPUT_TREE_JSON = r"P:\AI_Documentation\code_analysis.json"
OUTPUT_TREE_JSON = r"P:\AI_Documentation\annotated_code_analysis.json"

with open(INPUT_TREE_JSON, "r", encoding="utf-8") as f:
    tree = json.load(f)

walk_and_process(tree, BASE_REPO_PATH)

with open(OUTPUT_TREE_JSON, "w", encoding="utf-8") as f:
    json.dump(tree, f, indent=2, ensure_ascii=False)

print(f"\n Enhanced JSON saved to: {OUTPUT_TREE_JSON}")


