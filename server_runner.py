# Arc CLI - Server
import typer
from rich.console import Console
import config 
import datetime
from server_app import server_app, repo_url_to_name
from server_manager import update_local_server, commit_changes, upload_changes
import github_api
from constants import *

console = Console()  

@server_app.command("write-lock")
def write_lock_command():
    write_lock_file(config.load_config(CONFIG_FILE).get("server_address"))

def write_lock_file(server_address):
    update_local_server()
    if server_address is None:
        console.print("No server repository set. Please run 'arc server select' first.")
        return
    user, repo = repo_url_to_name(server_address)
    server_dir = config.DATA_DIR / "repositories" / user / repo
    lock_file = server_dir / "server.lock"
    if lock_file.exists():
        console.print(f"<red>ERROR</red>: Lock file already exists at {lock_file}. Server is already running.")
        return
    else:
        lock_data = {
            "status": "running",
            "locked_by": config.load_config(CONFIG_FILE).get("username", "unknown"),
            "timestamp": datetime.datetime.now().isoformat(),
        }
        lock_file.write_text(str(lock_data))
        console.print(f"Lock file created at {lock_file}. Server is now running.")
    commit_changes("Arc Server Lockfile Creation")
    upload_changes()

@server_app.command("remove-lock")
def remove_lock_command(
    force: bool = typer.Option(
        False,
        "--force",
        "-f",
        help="Force remove the lock file without checking for updates. Use with caution."
    )
):
    remove_lock(config.load_config(CONFIG_FILE).get("server_address"), force)
    

def remove_lock(server_address, force: bool = False):
    if server_address is None:
        console.print("No server repository set. Please run 'arc server select' first.")
        return
    user, repo = repo_url_to_name(server_address)
    server_dir = config.DATA_DIR / "repositories" / user / repo
    lock_file = server_dir / "server.lock"
    update_local_server()
    if lock_file.exists():
        jjson_data = eval(lock_file.read_text())
        locked_by = jjson_data.get("locked_by", "unknown")
        if locked_by != config.load_config(CONFIG_FILE).get("username", "unknown") and not force:
            console.print(f"<red>ERROR</red>: Lock file is owned by '{locked_by}'. Use --force to override.")
            return
        else:            
            lock_file.unlink()
            if not force:
                commit_changes("Arc Server Lockfile Removal")
            else:
                commit_changes("Arc Server Force Lockfile Removal")
            upload_changes()
            console.print(f"Lock file at {lock_file} removed. Server is now stopped.")
    else:
        console.print(f"No lock file found.")
        
def is_locked(server_address):
    update_local_server()
    if server_address is None:
        console.print("No server repository set. Please run 'arc server select' first.")
        return False
    user, repo = repo_url_to_name(server_address)
    server_dir = config.DATA_DIR / "repositories" / user / repo
    lock_file = server_dir / "server.lock"
    return lock_file.exists() 

def run_server():
    config_data = config.load_config(CONFIG_FILEbb)
    server_address = config_data.get("server_address")
    if server_address is None:
        console.print("No server repository set. Please run 'arc server select' first.")
        return
    if is_locked(server_address):
        console.print("Server is already running. Please stop it before starting a new one.")
        return
    user, repo = repo_url_to_name(server_address)
    server_dir = config.DATA_DIR / "repositories" / user / repo
    config_file = server_dir / "arcHost.config"
    if not config_file.exists():
        console.print("Server repository is not initialized. Please run 'arc server init' first.")
        return
    