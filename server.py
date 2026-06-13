# Arc CLI - Provider management
from importlib.resources import path
import subprocess
from urllib.parse import urlparse
import typer
from rich.console import Console
import config 
import datetime
import github_api
from repo import show_server
from pathlib import Path

server_app = typer.Typer()
console = Console()  

@server_app.command("current")
def show_current_server():
    show_server()

@server_app.command("download")
def download_server():
    update_local_server()
    
@server_app.command("fetch")
def update_local_server():
    repo_url = config.load_config().get("server_address")
    if repo_url is None:
        console.print("No server repository set. Please run 'arc server select' first.")
        return
    url_path = urlparse(repo_url).path.strip("/")
    user, repo = url_path.split("/")[:2]
    repository_path = config.DATA_DIR / "repositories" / user / repo
    if repository_path.exists():
        console.print(f"Updating local repository at {repository_path}")
        subprocess.run(["git", "-C", str(repository_path), "pull"], check=True)
    else:
        console.print(f"Downloading local repository at {repository_path}")
        clone_server_repo(config.get_keyring("https://github.com"), repo_url)
        return


def clone_server_repo(token: str, repo_url: str):
    token = config.get_keyring("https://github.com")
    if token is None:
        console.print("GitHub token not found. Please run 'arc provider setup' first.")
        return
    if repo_url is None:
        console.print("No server repository set. Please run 'arc server select' first.")
        return
    
    url_path = urlparse(repo_url).path.strip("/")
    user, repo = url_path.split("/")[:2]

    download_path = config.DATA_DIR / "repositories" / user / repo
    
    subprocess.run(["git", "clone", repo_url, str(download_path)], check=True)
    
    
@server_app.command("save")
def save_server():
    repo_url = config.load_config().get("server_address")
    if repo_url is None:
        console.print("No server repository set. Please run 'arc server select' first.")
        return
    url_path = urlparse(repo_url).path.strip("/")
    user, repo = url_path.split("/")[:2]
    repository_path = config.DATA_DIR / "repositories" / user / repo
    if not repository_path.exists():
        console.print(f"Local repository not found at {repository_path}. Please run 'arc server fetch' first.")
        return
    subprocess.run(["git", "-C", str(repository_path), "add", "."], check=True)
    subprocess.run(["git", "-C", str(repository_path), "commit", "-m", f"ArcHost Server Hosting Change - {datetime.datetime.now()}"], check=True)
    
@server_app.command("upload")
def upload_changes():
    repo_url = config.load_config().get("server_address")
    if repo_url is None:
        console.print("No server repository set. Please run 'arc server select' first.")
        return
    url_path = urlparse(repo_url).path.strip("/")
    user, repo = url_path.split("/")[:2]
    repository_path = config.DATA_DIR / "repositories" / user / repo
    if not repository_path.exists():
        console.print(f"Local repository not found at {repository_path}. Please run 'arc server fetch' first.")
        return
    subprocess.run(["git", "-C", str(repository_path), "push"], check=True)