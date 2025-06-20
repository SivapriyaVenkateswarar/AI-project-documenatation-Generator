import os
import subprocess

os.chdir("P:/AI_Documentation/uml")

if not os.path.exists("plantuml.jar"):
    print("Downloading PlantUML...")
    subprocess.run([
        "curl",
        "-L",
        "-o",
        "plantuml.jar",
        "https://github.com/plantuml/plantuml/releases/latest/download/plantuml.jar"
    ])

print("Generating UML diagram...")
subprocess.run(["java", "-jar", "plantuml.jar", "combined_diagram.puml"])
print("Diagram generated")
