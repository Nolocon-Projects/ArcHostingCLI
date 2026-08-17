# Arc CLI - Server
import json
import subprocess
import typer
from rich.console import Console
import config 
import datetime
import github_api
from server_app import server_app, get_local_path
from constants import *
console = Console()

@server_app.callback(invoke_without_command=True)
def main(ctx: typer.Context):
    if ctx.invoked_subcommand is None:
        show_server()

@server_app.command("select")
def set_server_command(server_address):
    set_server(server_address)
    console.print(f"Server address set to: {server_address}")

def set_server(server_address: str):
    if server_address.endswith(".git"):
        server_address = server_address[:-4]
    cfg = {
        "server_address": server_address,
        "last_updated": datetime.datetime.now().isoformat()
    }
    config.save_config(CONFIG_FILE, cfg)
    
@server_app.command("deselect")
def deselect_server():
    cfg = config.load_config(CONFIG_FILE)
    if "server_address" in cfg:
        del cfg["server_address"]
        config.save_config(CONFIG_FILE, cfg)
        console.print("Server address deselected.")
    else:
        console.print("No server address set.")

@server_app.command("current")
def show_current_server():
    show_server()

def show_server():
    server_address = config.load_config(CONFIG_FILE).get("server_address")

    if server_address:
        console.print(f"Current Server Address: {server_address}")
    else:
        console.print("No Server Address set")
    
@server_app.command("fetch")
def update_local_server():
    repo_url = config.load_config(CONFIG_FILE).get("server_address")
    if repo_url is None:
        console.print("No server repository set. Please run 'arc server select' first.")
        return
    repository_path = get_local_path(repo_url)
    if repository_path.exists():
        console.print(f"Updating local repository at {repository_path}")
        subprocess.run(["git", "-C", str(repository_path), "pull"], check=True)
    else:
        console.print(f"Downloading local repository at {repository_path}")
        clone_server_repo(repo_url)
        return

@server_app.command("download")
def download_server():
    update_local_server()

def clone_server_repo(repo_url: str):
    try:
        config.get_keyring("https://github.com")
    except ValueError:
        console.print("GitHub token not found. Please run 'arc provider setup' first.")
        return
    if repo_url is None:
        console.print("No server repository set. Please run 'arc server select' first.")
        return
    
    download_path = get_local_path(repo_url)
    
    subprocess.run(["git", "clone", repo_url, str(download_path)], check=True)
    
    
    
@server_app.command("create")
def create_server_repo(
    name: str | None = None,
):
    token = config.get_keyring("https://github.com")
    if token is None:
        console.print(
            "GitHub token not found. Please run 'arc provider setup' first."
        )
        return
    if name is None:
        name = console.input("Server Repository Name: ")
    server_address = github_api.create_github_repo(
        token,
        name,
        private=True
    )
    console.print(
        f"Server Repository created: {server_address}"
    )
    set_server(server_address)
    update_local_server()
    init_server(server_address)
    
@server_app.command("init")
def init_server(server_address: str | None = None):
    if server_address is None:
        server_address = config.load_config(CONFIG_FILE).get("server_address")
        if server_address is None:
            console.print("No server repository set. Please run 'arc server select' first or provide a server address.")
            return
    server_dir = get_local_path(server_address)
    file = (
        server_dir
        / "arcHost.config"
    )
    file_data = {
        "version": APP_VERSION,
    }
    file.write_text(
        json.dumps(file_data, indent=4),
        encoding="utf-8"
    )
    commit_changes("Base ArcHost Config Creation")
    upload_changes()
    console.print("Server repository initialized.")
    
@server_app.command("invite")
def invite_user(username: str):
    repo_url = config.load_config(CONFIG_FILE).get("server_address")
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
    repo_url = config.load_config(CONFIG_FILE).get("server_address")
    if repo_url is None:
        console.print("No server repository set. Please run 'arc server select' first.")
        return
    repository_path = get_local_path(repo_url)
    if not repository_path.exists():
        console.print(f"Local repository not found at {repository_path}. Please run 'arc server fetch' first.")
        return
    subprocess.run(["git", "-C", str(repository_path), "add", "."], check=True)
    subprocess.run(["git", "-C", str(repository_path), "commit", "-m", f"{message} - {datetime.datetime.now()}"], check=True)
    
@server_app.command("upload")
def upload_changes():
    repo_url = config.load_config(CONFIG_FILE).get("server_address")
    if repo_url is None:
        console.print("No server repository set. Please run 'arc server select' first.")
        return
    repository_path = get_local_path(repo_url)
    if not repository_path.exists():
        console.print(f"Local repository not found at {repository_path}. Please run 'arc server fetch' first.")
        return
    subprocess.run(["git", "-C", str(repository_path), "push"], check=True)
    

@server_app.command("set-execution-command")
def set_execution_command(command: str | None = None):
    repo_url = config.load_config(CONFIG_FILE).get("server_address")
    if repo_url is None:
        console.print(
            "No server repository set. Please run 'arc server select' first."
        )
        return
    if command is None:
        command = console.input("Execution Command: ")
    server_dir = get_local_path(repo_url)
    config_file = server_dir / "arcHost.config"
    if not config_file.exists():
        console.print(
            "Server repository is not initialized. Please run 'arc server init' first."
        )
        return
    config_data = config.load_config(config_file)
    if not isinstance(config_data, dict):
        console.print("Invalid config format")
        return
    config_data["execution_command"] = command
    config.save_config(config_file, config_data)
    commit_changes("Updated Server Execution Command")
    upload_changes()
    console.print(f"Execution command set to: {command}")