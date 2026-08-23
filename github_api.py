import time
import requests
import webbrowser
import platform
import subprocess
import shutil
from rich.console import Console
from urllib.parse import urlparse
from pathlib import Path
from constants import GH_CLIENT_ID as CLIENT_ID

console = Console()

def copy_to_clipboard(text: str) -> bool:
    system = platform.system().lower()

    try:
        # Windows
        if system == "windows":
            subprocess.run(
                "clip",
                input=text.encode(),
                shell=True,
                check=True
            )
            return True

        # macOS
        if system == "darwin":
            subprocess.run(
                ["pbcopy"],
                input=text.encode(),
                check=True
            )
            return True

        # Linux (wl-copy)
        if system == "linux":
            if shutil.which("wl-copy"):
                subprocess.run(
                    ["wl-copy"],
                    input=text.encode(),
                    check=True
                )
                return True

            if shutil.which("xclip"):
                subprocess.run(
                    ["xclip", "-selection", "clipboard"],
                    input=text.encode(),
                    check=True
                )
                return True

            if shutil.which("xsel"):
                subprocess.run(
                    ["xsel", "--clipboard", "--input"],
                    input=text.encode(),
                    check=True
                )
                return True

        return False

    except Exception:
        return False


def prompt_github_token_oauth() -> str:
    response = requests.post(
        "https://github.com/login/device/code",
        headers={"Accept": "application/json"},
        data={
            "client_id": CLIENT_ID,
            "scope": "repo",
        },
        timeout=30,
    )

    response.raise_for_status()
    data = response.json()

    device_code = data["device_code"]
    user_code = data["user_code"]
    verification_uri = data["verification_uri"]
    interval = data.get("interval", 5)

    webbrowser.open(verification_uri)

    copied = copy_to_clipboard(user_code)

    console.print("\nGitHub Login login required")
    console.print(f"Please open {verification_uri}")

    if copied:
        console.print("The code has been copied to clipboard")
    else:
        console.print(f"Code: {user_code}")

    while True:
        time.sleep(interval)

        token_response = requests.post(
            "https://github.com/login/oauth/access_token",
            headers={"Accept": "application/json"},
            data={
                "client_id": CLIENT_ID,
                "device_code": device_code,
                "grant_type": "urn:ietf:params:oauth:grant-type:device_code",
            },
            timeout=30,
        )

        token_response.raise_for_status()
        result = token_response.json()

        if "access_token" in result:
            return result["access_token"]

        error = result.get("error")

        if error == "authorization_pending":
            continue

        if error == "slow_down":
            interval += 5
            continue

        if error == "expired_token":
            raise RuntimeError("Device code expired")

        if error == "access_denied":
            raise RuntimeError("Login denied")

        raise RuntimeError(f"OAuth failed: {result}")

def create_github_repo(token: str, name: str, private: bool = False) -> str:
    url = "https://api.github.com/user/repos"

    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json"
    }

    payload = {
        "name": name,
        "private": private,
        "auto_init": True
    }

    response = requests.post(url, headers=headers, json=payload, timeout=30)

    response.raise_for_status()

    data = response.json()

    return data["clone_url"]

def invite_collaborator(token: str, repo_url: str, username: str, permission: str = "push") -> None:
    path = urlparse(repo_url).path.strip("/")

    owner, repo = path.split("/")[:2]

    url = f"https://api.github.com/repos/{owner}/{repo}/collaborators/{username}"

    r = requests.put(
        url,
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json"
        },
        json={"permission": permission},
        timeout=30
    )

    if r.status_code not in (201, 204):
        print("STATUS:", r.status_code)
        print("BODY:", r.text)

    r.raise_for_status()

def get_github_username(token: str) -> str:
    """
    Returns the GitHub username for a given personal access token.
    """

    if not token:
        raise ValueError("Token is required")

    url = "https://api.github.com/user"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json"
    }

    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        raise RuntimeError(
            f"GitHub API error {response.status_code}: {response.text}"
        )

    data = response.json()

    return data.get("login")


def add_large_files_to_lfs(repository_path: Path, min_size_mib: int = 100):

    repository_path = Path(repository_path)
    min_size_bytes = min_size_mib * 1024 * 1024

    # Make sure Git LFS is initialized for this repository.
    subprocess.run(
        ["git", "-C", str(repository_path), "lfs", "install"],
        check=True
    )

    for path in repository_path.rglob("*"):
        if not path.is_file():
            continue

        # Ignore files inside .git.
        if ".git" in path.parts:
            continue

        if path.stat().st_size < min_size_bytes:
            continue

        relative_path = path.relative_to(repository_path).as_posix()

        subprocess.run(
            [
                "git",
                "-C",
                str(repository_path),
                "lfs",
                "track",
                relative_path
            ],
            check=True
        )