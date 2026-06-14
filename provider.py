# Arc CLI - Provider management
import subprocess
import typer
from rich.console import Console
import config 
import datetime
import github_api  
provider_app = typer.Typer()
console = Console()


def git_config_get(key: str) -> str:
    result = subprocess.run(
        ["git", "config", "--get", key],
        capture_output=True,
        text=True
    )
    return result.stdout.strip()



@provider_app.command("show-current")
def show_provider():
    provider = config.load_config().get("provider_url")

    if provider:
        console.print(f"Current Provider URL: {provider}")
    else:
        console.print("No Provider URL set")
        
        
def init_provider_cfg(provider_url: str, token):
    provider_cfg = {
        "provider_url": provider_url,
        "username": github_api.get_github_username(token),
        "last_updated": datetime.datetime.now().isoformat()
    }
    config.save_keyring(provider_url, token)
    config.save_config(provider_cfg)

def load_provider_cfg():
    cfg = config.load_config()
    provider_url = cfg.get("provider_url")
    if not provider_url:
        raise ValueError("Provider URL not found in config")
    token = config.get_keyring(provider_url)
    return cfg.get("provider_url"), token


@provider_app.command("setup")
def init_provider():
    provider_url = console.input("Default Upload Provider: (Leave blank for default): ")
    if not provider_url:
        provider_url = "https://github.com"
    else:
        console.print(f"Sorry, custom providers aren't supported yet.")
        return
    if provider_url.endswith("/"):
        provider_url = provider_url[:-1]
        
    if provider_url == "https://github.com":
        token = github_api.prompt_github_token_oauth()
    else:
        token = console.input("Personal Access Token: (Leave blank for none): ")
        
    init_provider_cfg(provider_url, token)
    console.print("Provider initialized with provider URL and token")
    
def delete_token(provider_url):
    config.delete_keyring(provider_url)