# Arc CLI Configuration management
import json
import keyring
from constants import *


def load_config(file):
    if not file.exists():
        return {}
    try:
        return json.loads(file.read_text())
    except (json.JSONDecodeError, OSError):
        return {}

def save_config(file, updates: dict):
    file.parent.mkdir(parents=True, exist_ok=True)

    # Vorhandene Config laden
    if file.exists():
        try:
            config = json.loads(file.read_text())
        except (json.JSONDecodeError, OSError):
            config = {}
    else:
        config = {}

    # Neue Werte einfügen/überschreiben
    config.update(updates)

    # Gesamte Config zurückschreiben
    file.write_text(json.dumps(config, indent=4))


def save_keyring(name: str, key: str):
    keyring.set_password("ArcHosting", name, key)  

def get_keyring(name: str) -> str:
    # Return None when not found to allow callers to handle missing tokens
    # without relying on exceptions for control flow.
    value = keyring.get_password("ArcHosting", name)
    return value

def delete_keyring(name: str):
    keyring.delete_password("ArcHosting", name)