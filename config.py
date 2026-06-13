# Arc CLI Configuration management
import json
from pathlib import Path
import keyring

DATA_DIR = Path.home() / ".arccli"
CONFIG_FILE = DATA_DIR / "config.json"


def load_config():
    if not CONFIG_FILE.exists():
        return {}
    try:
        return json.loads(CONFIG_FILE.read_text())
    except Exception:
        return {}

def save_config(data: dict):
    CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
    CONFIG_FILE.write_text(json.dumps(data, indent=4))
    CONFIG_FILE.write_text(json.dumps(data, indent=4))


def save_keyring(name: str, key: str):
    keyring.set_password("ArcHosting", name, key)  

def get_keyring(name: str) -> str:
    value = keyring.get_password("ArcHosting", name)
    if value is None:
        raise ValueError(f"Key '{name}' not found in keyring")
    return value