from git import Repo
import os

def clone_repo(git_url, clone_dir="cloned_repo"):
    if os.path.exists(clone_dir):
        print(f"Deleting existing directory {clone_dir}")
        os.system(f"rm -rf {clone_dir}")
    Repo.clone_from(git_url, clone_dir)
    print(f"Cloned {git_url} into {clone_dir}")
