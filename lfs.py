from pathlib import Path


def get_oversized_files(directory, min_size_mb):
    min_size = min_size_mb * 1024 * 1024

    for path in Path(directory).rglob("*"):
        if path.is_file() and path.stat().st_size > min_size:
            yield path
