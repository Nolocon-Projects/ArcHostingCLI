from pathlib import Path


def get_oversized_files(directory, min_size_mb):
    min_size = min_size_mb * 1024 * 1024

    for path in Path(directory).rglob("*"):
        if path.is_file() and path.stat().st_size > min_size:
            yield path


def split_file(file_path, delete_afterwards=False, max_chunk_size_mb=50):
    chunk_size = max_chunk_size_mb * 1024 * 1024

    file_path = Path(file_path)

    if not file_path.is_file():
        raise FileNotFoundError(f"File Not Found: {file_path}")

    part_number = 1

    with file_path.open("rb") as source:
        while True:
            data = source.read(chunk_size)

            if not data:
                break

            part_path = file_path.parent / f"{file_path.name}.part{part_number:02d}"

            with part_path.open("wb") as part:
                part.write(data)

            part_number += 1

    if delete_afterwards:
        file_path.unlink()

    print(f"File successfully split into {part_number - 1} parts.")


def merge_files(path, filename, delete_afterwards=False, buffer_size_mb=50):
    path = Path(path)
    output_path = path / filename
    buffer_size = buffer_size_mb * 1024 * 1024

    parts = []
    part_number = 1

    while True:
        part_path = path / f"{filename}.part{part_number:02d}"

        if not part_path.is_file():
            break

        parts.append(part_path)
        part_number += 1

    if not parts:
        raise FileNotFoundError(
            f"No parts found for '{filename}'."
        )

    expected = 1

    for part in parts:
        current = int(part.name.rsplit(".part", 1)[1])

        if current != expected:
            raise ValueError(
                f"Missing Part: {filename}.part{expected:02d}"
            )

        expected += 1

    with output_path.open("wb") as output:
        for part_path in parts:
            with part_path.open("rb") as part:
                while chunk := part.read(buffer_size):
                    output.write(chunk)

    if delete_afterwards:
        for part_path in parts:
            part_path.unlink()

    print(f"File successfully merged from {len(parts)} parts.")