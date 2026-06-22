# Arc CLI - A command-line tool for managing Arc repositories
from urllib.parse import urlparse

import typer
from rich.console import Console
from rich.panel import Panel
from constants import *
app = typer.Typer()
console = Console()

# Initalize Subcommands
from provider import provider_app
app.add_typer(provider_app, name="provider")


from server_app import server_app
import server_manager
import server_runner
app.add_typer(server_app, name="server")


BRAND = r"""
  ▄▄▄▄                ▄▄▄▄▄▄▄ ▄▄▄      ▄▄▄▄▄
▄██▀▀██▄             ███▀▀▀▀▀ ███       ███
███  ███ ████▄ ▄████ ███      ███       ███
███▀▀███ ██ ▀▀ ██    ███      ███       ███
███  ███ ██    ▀████ ▀███████ ████████ ▄███▄
"""


def show_home():
    console.print(Panel.fit(BRAND, title="ArcCLI", subtitle=f"v{APP_VERSION}"))
    console.print("PLACEHOLDER")


@app.callback(invoke_without_command=True)
def main(ctx: typer.Context):
    if ctx.invoked_subcommand is None:
        show_home()


@app.command()
def version():
    console.print(f"ArcCLI v{APP_VERSION}")

@app.command()
def about():
    show_home()

if __name__ == "__main__":
    app()