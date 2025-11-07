from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional
import os

from clone_utils import clone_and_analyze_repo
from process_repo_full import process_repo_full
from UML_diag import generate_uml_diagram_from_markdown

# ----------------------------------------------------
# Initialize FastAPI App
# ----------------------------------------------------
app = FastAPI(
    title="AI Documentation Backend",
    description=(
        "Backend service for repository cloning, analysis, Gemini-based documentation, "
        "UML generation, and complete project overview."
    ),
    version="2.0.0",
)

# ----------------------------------------------------
# Enable CORS (for frontend-backend communication)
# ----------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ----------------------------------------------------
# Serve UML PNGs statically
# ----------------------------------------------------
uml_output_dir = os.path.abspath(r"P:\AI_Documentation\example\uml")
os.makedirs(uml_output_dir, exist_ok=True)
app.mount("/uml", StaticFiles(directory=uml_output_dir), name="uml")

# ----------------------------------------------------
# Request Models
# ----------------------------------------------------
class RepoRequest(BaseModel):
    git_url: str


class UMLRequest(BaseModel):
    markdown_path: Optional[str] = None
    output_dir: Optional[str] = None
    render_png: Optional[bool] = True


# ----------------------------------------------------
# Routes
# ----------------------------------------------------
@app.get("/")
def home():
    """Simple health check endpoint."""
    return {
        "status": "Backend running successfully",
        "version": "2.0.0",
        "features": [
            "Clone and analyze repositories",
            "Generate Gemini-based documentation",
            "Create UML diagrams",
            "Build unified project overview"
        ],
    }


@app.post("/clone_and_analyze")
def clone_and_analyze(req: RepoRequest):
    """Clone a GitHub repo and perform initial analysis."""
    try:
        result = clone_and_analyze_repo(req.git_url)
        return {
            "status": "success",
            "message": "Repository cloned and analyzed successfully",
            "analysis": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Clone/analysis failed: {str(e)}")


@app.post("/generate_uml")
def generate_uml(req: UMLRequest):
    """Generate a UML diagram from markdown documentation."""
    try:
        uml_path = generate_uml_diagram_from_markdown(
            markdown_path=req.markdown_path,
            output_dir=req.output_dir,
            render_png=req.render_png
        )
        return {
            "status": "success",
            "message": "UML diagram generated successfully",
            "uml_path": uml_path
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"UML generation failed: {str(e)}")


@app.post("/process_repo")
def process_repo(req: RepoRequest):
    """Run full pipeline: clone, analyze, generate docs, and create overview."""
    try:
        # 1. Run the complete repository processing pipeline
        result = process_repo_full(req.git_url)

        # 2. Locate the generated markdown file
        markdown_path = result.get("markdown_path") or r"P:\AI_Documentation\example\FULL_PROJECT_DOC.md"
        if not os.path.exists(markdown_path):
            raise HTTPException(status_code=500, detail="Markdown file not found after processing")

        # 3. Read markdown content
        with open(markdown_path, "r", encoding="utf-8") as f:
            project_doc_text = f.read()

        # 4. Generate UML diagram (optional)
        uml_path = None
        uml_puml_path = generate_uml_diagram_from_markdown()
        if os.path.exists(uml_puml_path):
            uml_filename = os.path.basename(uml_puml_path).replace(".puml", ".png")
            uml_path = f"/uml/{uml_filename}"

        # 5. Return results
        return {
            "status": "success",
            "message": "Repository processed successfully",
            "details": {
                "project_doc_text": project_doc_text,
                "uml_url": uml_path,
                "other_info": result
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Repository processing failed: {str(e)}")
