import os
import json

def export_markdown_from_tree(tree, output_md_path="code_documentation.md"):
    md_lines = ["# Code Documentation Summary\n"]

    def write_md(file_info):

        md_lines.append("\n### Summary")
        summary = file_info.get("summary")
        if summary:
            md_lines.append(summary)
        else:
            md_lines.append("> No summary available.")


    def recurse(node):
        if node["type"] == "file" and node["name"].endswith(".py"):
            write_md(node)
        elif node["type"] == "folder":
            md_lines.append(f"\n# Folder: {node['name']}")
            for child in node.get("children", []):
                recurse(child)

    recurse(tree)

    with open(output_md_path, "w", encoding="utf-8") as f:
        f.write("\n".join(md_lines))

    print(f"Markdown documentation exported to: {output_md_path}")

if __name__ == "__main__":
    with open("annotated_code_analysis.json", "r", encoding="utf-8") as f:
        tree_data = json.load(f)

    export_markdown_from_tree(tree_data, output_md_path="complete_code_summary.md")
