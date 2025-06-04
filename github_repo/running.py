from cloning_github import clone_repo
from metadata_directory import build_tree_with_metadata
from saving import save_structure

if __name__ == "__main__":
    url = "https://github.com/SivapriyaVenkateswarar/ThreatLens"
    clone_repo(url)
    struct = build_tree_with_metadata("P:\AI_Documentation\github_repo\cloned_repos")
    save_structure(struct)
