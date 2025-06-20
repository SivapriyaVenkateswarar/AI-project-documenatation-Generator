import os
import google.generativeai as genai

genai.configure(api_key="AIzaSyAV9KOb6L2eB-a7W-3imCSTGzVvc7ynViw")  

COMBINED_MARKDOWN = "complete_code_summary.md"  
PLANTUML_DIR = "uml"
OUTPUT_FILE = "combined_diagram.puml"  

os.makedirs(PLANTUML_DIR, exist_ok=True)

PROMPT_TEMPLATE = """You are an expert UML documentation assistant.

Given the following documentation summary of a multi-file Python project, your task is to:

1. Understand the **overall purpose** and **user-facing functionality** of the application.
2. Generate a **PlantUML use case diagram** from the perspective of **end users**, ignoring internal Python functions, methods, and implementation details.
3. Focus on showing **how different user roles interact** with the system.
4. Keep the diagram **simple, clear, and suitable for non-CS stakeholders**.
5. Use `@startuml` and `@enduml` to wrap the code, and return only the UML code block.

---
{markdown_content}
"""

model = genai.GenerativeModel("models/gemini-1.5-flash")

def generate_plantuml(md_text):
    prompt = PROMPT_TEMPLATE.format(markdown_content=md_text)
    response = model.generate_content(prompt)
    return response.text.strip()

def extract_uml_block(text):
    if "```plantuml" in text:
        return text.split("```plantuml")[1].split("```")[0].strip()
    return text

def process_combined_file():
    with open(COMBINED_MARKDOWN, "r", encoding="utf-8") as f:
        content = f.read()

    print(f"[+] Processing combined markdown file: {COMBINED_MARKDOWN}")
    try:
        gemini_response = generate_plantuml(content)
        uml_code = extract_uml_block(gemini_response)

        uml_path = os.path.join(PLANTUML_DIR, OUTPUT_FILE)
        with open(uml_path, "w", encoding="utf-8") as f:
            f.write("@startuml\n")
            f.write(uml_code)
            f.write("\n@enduml")

        print(f"[✔] UML diagram saved to: {uml_path}")
    except Exception as e:
        print(f"[!] Error: {e}")

process_combined_file()
