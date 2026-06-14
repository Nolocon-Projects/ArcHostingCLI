# Arc CLI - Server
import subprocess
import typer
from rich.console import Console
import config 
import datetime
import github_api
from server_app import server_app, repo_url_to_name
console = Console()  

@server_app.callback(invoke_without_command=True)
def main(ctx: typer.Context):
    if ctx.invoked_subcommand is None:
        show_server()

@server_app.command("select")
def set_server_command(server_address):
    set_server(server_address)
    console.print(f"Server address set to: {server_address}")
    # Check if local Snapshot exists
    repo_url = config.load_config().get("server_address")
    if repo_url is None:
        console.print("No server repository set. Please run 'arc server select' first.")
        return
    user, repo = repo_url_to_name(repo_url)
    repository_path = config.DATA_DIR / "repositories" / user / repo
    if repository_path.exists():
        console.print(f"Local repository already exists at {repository_path}")
    else:
        console.print(f"No local repository found at {repository_path}. You can run 'arc server fetch' to download the repository.")

def set_server(server_address: str):
    if server_address.endswith(".git"):
        server_address = server_address[:-4]
    cfg = {
        "server_address": server_address,
        "last_updated": datetime.datetime.now().isoformat()
    }
    config.save_config(cfg)
    
@server_app.command("deselect")
def deselect_server():
    cfg = config.load_config()
    if "server_address" in cfg:
        del cfg["server_address"]
        config.save_config(cfg)
        console.print("Server address deselected.")
    else:
        console.print("No server address set.")

@server_app.command("current")
def show_current_server():
    show_server()

def show_server():
    server_address = config.load_config().get("server_address")

    if server_address:
        console.print(f"Current Server Address: {server_address}")
    else:
        console.print("No Server Address set")
    
@server_app.command("fetch")
def update_local_server():
    repo_url = config.load_config().get("server_address")
    if repo_url is None:
        console.print("No server repository set. Please run 'arc server select' first.")
        return
    user, repo = repo_url_to_name(repo_url)
    repository_path = config.DATA_DIR / "repositories" / user / repo
    if repository_path.exists():
        console.print(f"Updating local repository at {repository_path}")
        subprocess.run(["git", "-C", str(repository_path), "pull"], check=True)
    else:
        console.print(f"Downloading local repository at {repository_path}")
        clone_server_repo(config.get_keyring("https://github.com"), repo_url)
        return

@server_app.command("download")
def download_server():
    update_local_server()

def clone_server_repo(token: str, repo_url: str):
    token = config.get_keyring("https://github.com")
    if token is None:
        console.print("GitHub token not found. Please run 'arc provider setup' first.")
        return
    if repo_url is None:
        console.print("No server repository set. Please run 'arc server select' first.")
        return
    
    user, repo = repo_url_to_name(repo_url)

    download_path = config.DATA_DIR / "repositories" / user / repo
    
    subprocess.run(["git", "clone", repo_url, str(download_path)], check=True)
    
    
    
@server_app.command("create")
def create_server_repo():
    token = config.get_keyring("https://github.com")
    if token is None:
        console.print("GitHub token not found. Please run 'arc provider setup' first.")
        return
    name = console.input("Server Repository Name: ")
    server_address = github_api.create_github_repo(token, name, private=True)
    console.print(f"Server Repository created: {server_address}")
    set_server(server_address)
    
    
@server_app.command("invite")
def invite_user(username: str):
    repo_url = config.load_config().get("server_address")
    permission = "push"
    token = config.get_keyring("https://github.com")
    if token is None:
        console.print("GitHub token not found. Please run 'arc provider setup' first.")
        return
    if not repo_url:
        console.print("Server repository not set. Please run 'arc server select' first.")
        return
    
    github_api.invite_collaborator(token, repo_url, username, permission)
    console.print(f"Collaborator invited to {repo_url}: {username}")
    console.print(f"{username} will get an E-Mail from GitHub shortly with the invitation.")
    console.print("If the user hasn't recieved the invitation, you can send them the following URL to accept the invitation:")
    console.print(f"{repo_url}/invitations")
    console.print("Note: The invitation will expire after 7 days if not accepted.")
    
@server_app.command("save")
def save_server():
    commit_changes("Arc Server Execution Changes")


def commit_changes(message: str = "No commit message provided"):
    repo_url = config.load_config().get("server_address")
    if repo_url is None:
        console.print("No server repository set. Please run 'arc server select' first.")
        return
    user, repo = repo_url_to_name(repo_url)
    repository_path = config.DATA_DIR / "repositories" / user / repo
    if not repository_path.exists():
        console.print(f"Local repository not found at {repository_path}. Please run 'arc server fetch' first.")
        return
    subprocess.run(["git", "-C", str(repository_path), "add", "."], check=True)
    subprocess.run(["git", "-C", str(repository_path), "commit", "-m", f"{message} - {datetime.datetime.now()}"], check=True)
    
@server_app.command("upload")
def upload_changes():
    repo_url = config.load_config().get("server_address")
    if repo_url is None:
        console.print("No server repository set. Please run 'arc server select' first.")
        return
    user, repo = repo_url_to_name(repo_url)
    repository_path = config.DATA_DIR / "repositories" / user / repo
    if not repository_path.exists():
        console.print(f"Local repository not found at {repository_path}. Please run 'arc server fetch' first.")
        return
    subprocess.run(["git", "-C", str(repository_path), "push"], check=True)
    

