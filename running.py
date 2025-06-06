from github_repo.cloning_github import clone_repo
from github_repo.metadata_directory import build_tree_with_metadata
from github_repo.saving import save_structure
from static_code_analysis.python import build_code_analysis_tree

if __name__ == "__main__":
    url = "https://github.com/SivapriyaVenkateswarar/ThreatLens"
    clone_repo(url)

    repo_path = r"P:\AI_Documentation\github_repo\cloned_repos"
    
    struct = build_tree_with_metadata(repo_path)
    #struct2 = build_code_analysis_tree(repo_path)

    save_structure(struct, filename="repo_structure.json")
    #save_structure(struct2, filename="code_analysis.json")
