# Arc CLI - Server
import subprocess
import json
import shlex

import typer
from rich.console import Console
import config 
import datetime
from server_app import server_app, get_local_path
from server_manager import update_local_server, commit_changes, upload_changes
from constants import *
from lfs import *

console = Console()  

@server_app.command("write-lock")
def write_lock_command():
    write_lock_file(config.load_config(CONFIG_FILE).get("server_address"))

def write_lock_file(server_address):
    update_local_server()
    if server_address is None:
        console.print("No server repository set. Please run 'arc server select' first.")
        return
    server_dir = get_local_path(server_address)
    if server_dir is None:
        raise RuntimeError("Server directory could not be determined")
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
        # Persist lock information as JSON for safe, consistent parsing.
        lock_file.write_text(json.dumps(lock_data), encoding="utf-8")
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
    server_dir = get_local_path(server_address)
    if server_dir is None:
        raise RuntimeError("Server directory could not be determined")
    lock_file = server_dir / "server.lock"
    update_local_server()
    if lock_file.exists():
        try:
            lock_data = json.loads(lock_file.read_text())
        except (ValueError, json.JSONDecodeError):
            console.print("<red>ERROR</red>: Invalid lock file format.")
            return
        if not isinstance(lock_data, dict):
            console.print("<red>ERROR</red>: Invalid lock file format.")
            return
        locked_by = lock_data.get("locked_by", "unknown")
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
    server_dir = get_local_path(server_address)
    if server_dir is None:
        raise RuntimeError("Server directory could not be determined")
    lock_file = server_dir / "server.lock"
    return lock_file.exists() 

@server_app.command("prepare")
def prepare_server_environment(server_directory):
    merge_all_splits(server_directory)    

@server_app.command("run")
def run_server():
    config_data = config.load_config(CONFIG_FILE)
    server_address = config_data.get("server_address")
    if server_address is None:
        console.print("No server repository set. Please run 'arc server select' first.")
        return
    if is_locked(server_address):
        console.print("Server is already running. Please stop it before starting a new one.")
        return
    server_dir = get_local_path(server_address)
    if server_dir is None:
            raise RuntimeError("Server directory could not be determined")
    config_file = server_dir / "arcHost.config"
    if not config_file.exists():
        console.print("Server repository is not initialized. Please run 'arc server init' first.")
        return
    write_lock_file(server_address)
    prepare_server_environment(server_dir)
    execution_command = config.load_config(config_file).get("execution_command")

    if not isinstance(execution_command, str):
        console.print("Invalid execution command in config")
        return
    # Show the command and require explicit confirmation before executing.
    console.print(f"Execution command: {execution_command}")
    confirm = console.input("Do you want to run this command? (y/N): ")
    if confirm.lower() != "y":
        console.print("Execution aborted by user.")
        return

    # Execute without shell to avoid shell injection risks. Split safely.
    try:
        cmd_list = shlex.split(execution_command)
        subprocess.run(cmd_list, shell=False, cwd=server_dir, check=True)
    except subprocess.CalledProcessError as e:
        console.print(f"Command failed with exit code {e.returncode}: {e}")
    except Exception as e:
        console.print(f"Failed to run command: {e}")
    # After execution, remove the lock file to indicate the server has stopped.
    remove_lock(server_address)