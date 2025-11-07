import os
import json
import shutil
import ast
import javalang
from git import Repo
from tree_sitter_languages import get_parser
import google.generativeai as genai
from dotenv import load_dotenv

# ------------------------------------------------------------------
# 1. Setup
# ------------------------------------------------------------------
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("GEMINI_API_KEY not found. Set in .env file.")

genai.configure(api_key=api_key)
model = genai.GenerativeModel("models/gemini-2.5-flash")

BASE_CLONE_DIR = r"P:\AI_Documentation\example\cloned_repo"
DOCS_DIR = r"P:\AI_Documentation\example\docs"
OUTPUT_MD = r"P:\AI_Documentation\example\FULL_PROJECT_DOC.md"
EXCLUDE_FOLDERS = {".git", "__pycache__", "node_modules", ".vscode", "venv"}

LANGUAGE_EXT_MAP = {
    "py": "python", "java": "java", "js": "javascript", "ts": "typescript",
    "cpp": "cpp", "c": "c", "cc": "cpp", "html": "html", "css": "css",
    "go": "go", "rb": "ruby", "php": "php"
}

# ------------------------------------------------------------------
# 2. Clone Repo
# ------------------------------------------------------------------
def clone_repo(git_url):
    if os.path.exists(BASE_CLONE_DIR):
        shutil.rmtree(BASE_CLONE_DIR, ignore_errors=True)
    Repo.clone_from(git_url, BASE_CLONE_DIR)
    print(f"Repo cloned: {git_url}")

# ------------------------------------------------------------------
# 3. Analyze Files
# ------------------------------------------------------------------
def analyze_file(file_path):
    ext = os.path.splitext(file_path)[1].lstrip(".").lower()
    if ext not in LANGUAGE_EXT_MAP:
        return None

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            source = f.read()
    except:
        source = ""

    analysis = {"lines": len(source.splitlines())}

    if ext == "py":
        try:
            tree = ast.parse(source)
            analysis.update({
                "classes": sum(isinstance(n, ast.ClassDef) for n in ast.walk(tree)),
                "functions": sum(isinstance(n, ast.FunctionDef) for n in ast.walk(tree)),
                "imports": [n.names[0].name for n in ast.walk(tree) if isinstance(n, ast.Import)]
            })
        except:
            pass
    elif ext == "java":
        try:
            tree = javalang.parse.parse(source)
            analysis.update({
                "classes": len(list(tree.filter(javalang.tree.ClassDeclaration))),
                "functions": len(list(tree.filter(javalang.tree.MethodDeclaration))),
                "imports": [imp.path for imp in tree.imports]
            })
        except:
            pass

    return {
        "path": os.path.relpath(file_path, BASE_CLONE_DIR),
        "ext": ext,
        "source": source[:2000],
        "analysis": analysis
    }

# ------------------------------------------------------------------
# 4. Collect All File Docs
# ------------------------------------------------------------------
def collect_all_files(base_dir):
    files_data = []
    for root, dirs, files in os.walk(base_dir):
        dirs[:] = [d for d in dirs if d not in EXCLUDE_FOLDERS]
        for file in files:
            path = os.path.join(root, file)
            data = analyze_file(path)
            if data:
                files_data.append(data)
    return files_data

# ------------------------------------------------------------------
# 5. Generate Full Markdown via Gemini
# ------------------------------------------------------------------
def generate_full_markdown_with_gemini(files_data):
    # Build a single prompt with everything
    prompt = "You are a technical documentation assistant.\n"
    prompt += "Generate a **full Markdown project document** with the following sections:\n"
    prompt += "1. Overview & Introduction\n2. System Architecture\n3. Functional Specification\n"
    prompt += "4. Non-Functional Requirements\n5. Code Documentation\n6. Testing\n7. Deployment / Execution\n"
    prompt += "8. User Guide\n9. Appendices\n\n"
    prompt += "Use the following per-file summaries as references.\n\n"

    for file in files_data:
        prompt += f"Filename: {file['path']}\n"
        prompt += f"Lines: {file['analysis'].get('lines','N/A')}\n"
        prompt += f"Classes: {file['analysis'].get('classes','N/A')}\n"
        prompt += f"Functions: {file['analysis'].get('functions','N/A')}\n"
        prompt += f"Imports: {file['analysis'].get('imports',[])}\n"
        prompt += f"Code (truncated):\n{file['source']}\n\n"

    prompt += "\nGenerate the Markdown content ready to save."

    response = model.generate_content(prompt)
    content = response.text.strip()

    # Save to file
    with open(OUTPUT_MD, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"[✔] Full project Markdown generated at: {OUTPUT_MD}")

# ------------------------------------------------------------------
# 6. Main Pipeline
# ------------------------------------------------------------------
def process_repo_full(git_url):
    clone_repo(git_url)
    files_data = collect_all_files(BASE_CLONE_DIR)
    generate_full_markdown_with_gemini(files_data)

    # Return the paths/info your frontend expects
    return {
        "markdown_path": OUTPUT_MD
    }

# ------------------------------------------------------------------
# Entry Point
# ------------------------------------------------------------------
if __name__ == "__main__":
    url = input("Enter GitHub repo URL: ").strip()
    process_repo_full(url)
