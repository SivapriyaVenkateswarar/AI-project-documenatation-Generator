import os
import subprocess
import google.generativeai as genai
from dotenv import load_dotenv

# --- Setup ---
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("GEMINI_API_KEY not set in .env")
genai.configure(api_key=api_key)
model = genai.GenerativeModel("models/gemini-2.5-flash")

# ===================================================
# UML (Flowchart) Generation Functions
# ===================================================

PROMPT_TEMPLATE = """You are an expert technical documentation assistant.

Given the following Markdown documentation summary of a multi-file Python project, your task is to:

1. Understand the **overall purpose** and **user-facing functionality** of the application.
2. Generate a **PlantUML activity diagram (flowchart)** representing the main workflow and processes.
3. Focus on **user actions, system decisions, and key process steps**.
4. Keep it **clear, concise, and non-technical** for stakeholders.
5. Return **only the PlantUML code**, wrapped between `@startuml` and `@enduml`.

---
{markdown_content}
"""

def generate_plantuml(md_text: str) -> str:
    """
    Generates PlantUML code (activity diagram / flowchart) from markdown using Gemini.
    """
    prompt = PROMPT_TEMPLATE.format(markdown_content=md_text)
    response = model.generate_content(prompt)
    return response.text.strip()

def extract_uml_block(text: str) -> str:
    """
    Extracts only the PlantUML code from Gemini's response.
    """
    if "```plantuml" in text:
        return text.split("```plantuml")[1].split("```")[0].strip()
    if "@startuml" in text and "@enduml" in text:
        return text.split("@startuml")[1].split("@enduml")[0].strip()
    return text

# ===================================================
# Main UML Generation Function
# ===================================================

def generate_uml_diagram_from_markdown(
    markdown_path: str = r"P:\AI_Documentation\example\FULL_PROJECT_DOC.md",
    output_dir: str = r"P:\AI_Documentation\example\uml",
    render_png: bool = True
) -> str:
    """
    Reads a Markdown documentation file and generates a PlantUML activity diagram (flowchart).
      - Uses Gemini to create PlantUML code
      - Saves .puml file
      - Optionally renders .png diagram using PlantUML
    """
    os.makedirs(output_dir, exist_ok=True)

    # Load Markdown summary
    with open(markdown_path, "r", encoding="utf-8") as f:
        md_text = f.read()

    print("[+] Generating UML (flowchart) with Gemini...")
    gemini_response = generate_plantuml(md_text)
    uml_code = extract_uml_block(gemini_response)

    puml_path = os.path.join(output_dir, "combined_diagram.puml")
    with open(puml_path, "w", encoding="utf-8") as f:
        f.write("@startuml\n")
        f.write(uml_code)
        f.write("\n@enduml")

    print(f"[✔] PlantUML flowchart saved to: {puml_path}")

    # Optionally render PNG
    if render_png:
        os.chdir(output_dir)
        if not os.path.exists("plantuml.jar"):
            print("[↓] Downloading PlantUML...")
            subprocess.run([
                "curl", "-L", "-o", "plantuml.jar",
                "https://github.com/plantuml/plantuml/releases/latest/download/plantuml.jar"
            ])
        print("Rendering flowchart PNG...")
        subprocess.run(["java", "-jar", "plantuml.jar", "combined_diagram.puml"])
        print("[✔] Flowchart PNG generated.")

    return puml_path
