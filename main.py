# Arc CLI - A command-line tool for managing Arc repositories
import typer
from rich.console import Console
from rich.panel import Panel

app = typer.Typer()
console = Console()

# Initalize Subcommands
from provider import provider_app
app.add_typer(provider_app, name="provider")
from repo import server_app
app.add_typer(server_app, name="repo")
from server import server_app
app.add_typer(server_app, name="server")

VERSION = "0.1.0"

BRAND = r"""
  ▄▄▄▄                ▄▄▄▄▄▄▄ ▄▄▄      ▄▄▄▄▄
▄██▀▀██▄             ███▀▀▀▀▀ ███       ███
███  ███ ████▄ ▄████ ███      ███       ███
███▀▀███ ██ ▀▀ ██    ███      ███       ███
███  ███ ██    ▀████ ▀███████ ████████ ▄███▄
"""


def show_home():
    console.print(Panel.fit(BRAND, title="ArcCLI", subtitle=f"v{VERSION}"))
    console.print("PLACEHOLDER")


@app.callback(invoke_without_command=True)
def main(ctx: typer.Context):
    if ctx.invoked_subcommand is None:
        show_home()


@app.command()
def version():
    console.print(f"ArcCLI v{VERSION}")

@app.command()
def about():
    show_home()
    
if __name__ == "__main__":
    app()