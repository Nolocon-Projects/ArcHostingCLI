from logging import config
import time
import requests
import webbrowser
import platform
import subprocess
import shutil
import typer
from rich.console import Console
import config
from urllib.parse import urlparse

CLIENT_ID = "Ov23liAVBP84OXx02dwF"

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
