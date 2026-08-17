from urllib.parse import urlparse
import typer
import config
from constants import CONFIG_FILE
server_app = typer.Typer()

def repo_url_to_name(repo_url: str):
    url_path = urlparse(repo_url).path.strip("/")
    user, repo = url_path.split("/")[:2]
    repo = repo.removesuffix(".git")
    return user, repo


def get_local_path(additional_weburl: str | None = None):
    repo_url = additional_weburl
    if repo_url is None:
        repo_url = config.load_config(CONFIG_FILE).get("server_address")
    if not repo_url:
        return None
    user, repo = repo_url_to_name(repo_url)
    return config.DATA_DIR / "repositories" / user / repo
# Don't dare touching me, unless you want to break the server commands. I am the glue that holds it all together.
# Without me, circular imports would break everything. Unless you don't get payed for that, it's not worth it. Just leave me alone, and let the server management commands work as intended.