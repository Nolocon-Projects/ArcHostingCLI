# Arc CLI - Repository management
import subprocess
import typer
from rich.console import Console
import config 
import datetime
repo_app = typer.Typer()
console = Console()
from github_token import prompt_github_token_oauth

get_config = config.load_config()
repository_path = config.DATA_DIR / "repositories"

def git_config_get(key: str) -> str:
    result = subprocess.run(
        ["git", "config", "--get", key],
        capture_output=True,
        text=True
    )
    return result.stdout.strip()

@repo_app.command("set")
def set_repo(url: str):

    get_config["repo_url"] = url
    config.save_config(get_config)

    console.print(f"Set repo: {url}")


@repo_app.command("get")
def show_repo():
    repo = get_config.get("repo_url")

    if repo:
        console.print(f"Current Repository: {repo}")
    else:
        console.print("No repo set")
        
        
        
@repo_app.command("validate")
def validate_repo():
    repo = get_config.get("repo_url")

    try:
        result = subprocess.run(["git", "ls-remote", repo],capture_output=True,text=True) # pyright: ignore[reportCallIssue, reportArgumentType]

        if result.returncode == 0:
            console.print("Repo valid")
            return True
        else:
            console.print("Repo invalid")
            console.print(result.stderr.strip())
            return False
        
    except FileNotFoundError:
        console.print("Git is not installed")
        return False

def init_server_cfg(server_url: str, token):
    server_cfg = {
        "server_url": server_url,
        "last_updated": datetime.datetime.now().isoformat()
    }
    config.save_keyring(server_url, token)
    config.save_config(server_cfg)


def load_server_cfg():
    cfg = config.load_config()
    server_url = cfg.get("server_url")
    if not server_url:
        raise ValueError("Server URL not found in config")
    token = config.get_keyring(server_url)
    return cfg.get("server_url"), token

@repo_app.command("setup")
def init_repository():
    server_url = console.input("Default Upload Server: (Leave blank for default): ")
    if not server_url:
        server_url = "https://github.com"
    if server_url.endswith("/"):
        server_url = server_url[:-1]
        
    if server_url == "https://github.com":
        token = prompt_github_token_oauth()
    else:
        token = console.input("Personal Access Token: (Leave blank for none): ")
        
    init_server_cfg(server_url, token)
    console.print("Server initialized with server URL and token")
    
