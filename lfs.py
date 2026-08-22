from pathlib import Path
import re


def merge_all_splits(directory):
    pattern = re.compile(r"^(.+)\.part\d+$")
    split_files = {}

    for path in Path(directory).rglob("*"):
        if not path.is_file():
            continue

        match = pattern.match(path.name)

        if not match:
            continue

        filename = match.group(1)

        split_files.setdefault(path.parent, set()).add(filename)

    for path, filenames in split_files.items():
        for filename in filenames:
            merge_files(
                path,
                filename,
                delete_afterwards=True
            )


def split_all_files(directory, max_chunk_size_mib):
    files = list(Path(directory).rglob("*"))

    for path in files:
        if path.is_file() and path.stat().st_size > max_chunk_size_mib * 1024 * 1024:
            split_file(
                path,
                delete_afterwards=True,
                max_chunk_size_mib=max_chunk_size_mib
            )


def get_oversized_files(directory, min_size_mib):
    min_size = min_size_mib * 1024 * 1024

    for path in Path(directory).rglob("*"):
        if path.is_file() and path.stat().st_size > min_size:
            yield path


def split_file(file_path, delete_afterwards=False, max_chunk_size_mib=50):
    chunk_size = max_chunk_size_mib * 1024 * 1024

    file_path = Path(file_path)

    if not file_path.is_file():
        raise FileNotFoundError(f"File Not Found: {file_path}")

    part_number = 1

    with file_path.open("rb") as source:
        while True:
            data = source.read(chunk_size)

            if not data:
                break

            part_path = (
                file_path.parent /
                f"{file_path.name}.part{part_number:02d}"
            )

            if part_path.exists():
                raise FileExistsError(
                    f"Part already exists: {part_path}"
                )

            with part_path.open("wb") as part:
                part.write(data)

            part_number += 1

    if delete_afterwards:
        file_path.unlink()

    print(
        f"File successfully split into "
        f"{part_number - 1} parts."
    )


def merge_files(
    path,
    filename,
    delete_afterwards=False,
    buffer_size_mb=50
):
    path = Path(path)
    output_path = path / filename
    buffer_size = buffer_size_mb * 1024 * 1024

    pattern = re.compile(
        rf"^{re.escape(filename)}\.part(\d+)$"
    )

    parts = []

    for part_path in path.iterdir():
        if not part_path.is_file():
            continue

        match = pattern.match(part_path.name)

        if not match:
            continue

        part_number = int(match.group(1))
        parts.append((part_number, part_path))

    if not parts:
        raise FileNotFoundError(
            f"No parts found for '{filename}'."
        )

    parts.sort(key=lambda item: item[0])

    for expected, (part_number, _) in enumerate(parts, start=1):
        if part_number != expected:
            raise ValueError(
                f"Missing Part: "
                f"{filename}.part{expected:02d}"
            )

    if output_path.exists():
        raise FileExistsError(
            f"Output file already exists: {output_path}"
        )

    with output_path.open("wb") as output:
        for _, part_path in parts:
            with part_path.open("rb") as part:
                while chunk := part.read(buffer_size):
                    output.write(chunk)

    if delete_afterwards:
        for _, part_path in parts:
            part_path.unlink()

    print(
        f"File successfully merged from "
        f"{len(parts)} parts."
    )