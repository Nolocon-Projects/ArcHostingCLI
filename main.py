# Arc CLI - A command-line tool for managing Arc repositories
import typer
from rich.console import Console
from rich.panel import Panel

app = typer.Typer()
console = Console()

# Initalize Subcommands
from repo import repo_app
app.add_typer(repo_app, name="repo")


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
    console.print("repo set <url>")
    console.print("repo show")
    console.print("version")


@app.callback(invoke_without_command=True)
def main(ctx: typer.Context):
    if ctx.invoked_subcommand is None:
        show_home()


@app.command()
def version():
    console.print(f"ArcCLI v{VERSION}")


if __name__ == "__main__":
    app()