import os
import json

def export_markdown_from_tree(tree, base_dir="."):
    def write_md(file_info):
        print(file_info)
        md_lines = []
        md_lines.append(f"# {file_info['name']}\n")
        md_lines.append(f"**Path**: {file_info['path']}")
        md_lines.append(f"**Lines of Code**: {file_info.get('lines_of_code', 'N/A')}")
        md_lines.append(f"**Classes**: {file_info.get('classes_count', 'N/A')}")
        md_lines.append(f"**Functions**: {file_info.get('functions_count', 'N/A')}")
        md_lines.append(f"**Imports**: {', '.join(file_info.get('imports', []))}\n")
        
        md_lines.append("---\n")
        md_lines.append("### Summary")
        md_lines.append("### Summary")
        summary = file_info.get("summary")
        analysis=file_info.get("analysis")
        if summary:
            md_lines.append(summary)  
        else:
            md_lines.append("> *No summary available* (will be updated by Gemini)")

        md_lines.append("### analysis")
        md_lines.append("### analysis")

        if analysis:
            md_lines.append(analysis)  
        else:
            md_lines.append("> *No analysis available* (will be updated by Gemini)")

        md_lines.append("\n---\n")
        md_lines.append("### UML Diagram")
        md_lines.append("*To be added after PlantUML integration*\n")

        md_path = os.path.join(base_dir, file_info["path"] + ".md")
        os.makedirs(os.path.dirname(md_path), exist_ok=True)
        with open(md_path, "w", encoding="utf-8") as f:
            f.write("\n".join(md_lines))

    def recurse(node):
        if node["type"] == "file" and node["name"].endswith(".py"):
            write_md(node)
        elif node["type"] == "folder":
            for child in node.get("children", []):
                recurse(child)

    recurse(tree)

with open("annotated_code_analysis.json", "r", encoding="utf-8") as f:
    tree_data = json.load(f)

export_markdown_from_tree(tree_data)
