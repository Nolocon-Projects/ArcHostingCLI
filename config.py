# Arc CLI Configuration management
import json
from pathlib import Path
import keyring

DATA_DIR = Path.home() / ".arcHost"
CONFIG_FILE = DATA_DIR / "config.json"


def load_config():
    if not CONFIG_FILE.exists():
        return {}
    try:
        return json.loads(CONFIG_FILE.read_text())
    except Exception:
        return {}
import json

def save_config(updates: dict):
    CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)

    # Vorhandene Config laden
    if CONFIG_FILE.exists():
        try:
            config = json.loads(CONFIG_FILE.read_text())
        except (json.JSONDecodeError, OSError):
            config = {}
    else:
        config = {}

    # Neue Werte einfügen/überschreiben
    config.update(updates)

    # Gesamte Config zurückschreiben
    CONFIG_FILE.write_text(json.dumps(config, indent=4))


def save_keyring(name: str, key: str):
    keyring.set_password("ArcHosting", name, key)  

def get_keyring(name: str) -> str:
    value = keyring.get_password("ArcHosting", name)
    if value is None:
        raise ValueError(f"Key '{name}' not found in keyring")
    return value

def delete_keyring(name: str):
    keyring.delete_password("ArcHosting", name)