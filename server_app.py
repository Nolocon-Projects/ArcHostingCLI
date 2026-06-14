from urllib.parse import urlparse
import typer
server_app = typer.Typer()

def repo_url_to_name(repo_url: str):
    url_path = urlparse(repo_url).path.strip("/")
    user, repo = url_path.split("/")[:2]
    return user, repo
# Don't dare touching me, unless you want to break the server commands. I am the glue that holds it all together.
# Without me, circular imports would break everything. Unless you don't get payed for that, it's not worth it. Just leave me alone, and let the server management commands work as intended.