# Arc CLI - Provider management
import subprocess
import typer
from rich.console import Console
import config 
import datetime

server_app = typer.Typer()
console = Console()
import github_api  

def set_server(server_address: str):
    if server_address.endswith(".git"):
        server_address = server_address[:-4]
    cfg = {
        "server_address": server_address,
        "last_updated": datetime.datetime.now().isoformat()
    }
    config.save_config(cfg)

@server_app.command("select")
def set_server_command(server_address):
    set_server(server_address)
    console.print(f"Server address set to: {server_address}")

@server_app.command("show-current")
def show_server():
    server_address = config.load_config().get("server_address")

    if server_address:
        console.print(f"Current Server Address: {server_address}")
    else:
        console.print("No Server Address set")

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