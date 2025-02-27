python
from github import Github
from datetime import datetime, timedelta
import os

# Constants
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")  # Set your GitHub token as an environment variable
TW = 365  # Time window in days (1 year)
MASTER_REPO_LIST = "masterRepoList.txt"

# Initialize GitHub API
g = Github(GITHUB_TOKEN)

def get_repo_list():
    """Read the list of repositories from masterRepoList.txt."""
    with open(MASTER_REPO_LIST, "r") as file:
        return [line.strip() for line in file.readlines()]

def get_stale_branches(repo, time_window):
    """Identify branches older than the time window."""
    stale_branches = []
    for branch in repo.get_branches():
        last_commit_date = branch.commit.commit.author.date
        if (datetime.now() - last_commit_date).days > time_window:
            stale_branches.append(branch.name)
    return stale_branches

def delete_branches(repo, branches_to_delete):
    """Delete selected branches."""
    for branch in branches_to_delete:
        ref = repo.get_git_ref(f"heads/{branch}")
        ref.delete()
        print(f"Deleted branch: {branch}")

def main():
    # Read repository list
    repo_urls = get_repo_list()
    deleted_branches_summary = {}

    for repo_url in repo_urls:
        repo_name = repo_url.split("/")[-1]
        repo = g.get_repo(f"github/{repo_name}")

        # Get stale branches
        stale_branches = get_stale_branches(repo, TW)
        print(f"Repository: {repo_name}")
        print(f"Total branches: {repo.get_branches().totalCount}")
        print(f"Stale branches: {len(stale_branches)}")

        if stale_branches:
            print("Stale branches:")
            for i, branch in enumerate(stale_branches, 1):
                print(f"{i}. {branch}")

            # Get user consent for deletion
            user_input = input("Enter branch numbers to delete (comma-separated, or 'all' to delete all, 'none' to skip): ")
            if user_input.lower() == "all":
                branches_to_delete = stale_branches
            elif user_input.lower() == "none":
                branches_to_delete = []
            else:
                selected_indices = [int(i) - 1 for i in user_input.split(",")]
                branches_to_delete = [stale_branches[i] for i in selected_indices]

            # Delete branches
            if branches_to_delete:
                delete_branches(repo, branches_to_delete)
                deleted_branches_summary[repo_name] = branches_to_delete

    # Generate executive summary
    print("\nExecutive Summary:")
    for repo, branches in deleted_branches_summary.items():
        print(f"Repository: {repo}")
        print(f"Deleted branches: {', '.join(branches)}")
        if len(branches) == repo.get_branches().totalCount:
            print("Recommendation: Delete the repository as all branches are stale.")

if __name__ == "__main__":
    main()
