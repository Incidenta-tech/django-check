import argparse
import shutil
import tempfile
from collections.abc import Sequence
from contextlib import closing

LOCATION_START = "#: "
FILE = "file"
NEVER = "never"


def _extract_location_file_name(line):
    file_names = line.rstrip().replace(LOCATION_START, "").split(" ")
    return sorted({n.split(":")[0] for n in file_names})


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("filenames", nargs="*", help="Filenames to process")
    parser.add_argument("--add-location", choices=[FILE, NEVER], required=False, default=FILE)
    args = parser.parse_args(argv)
    add_location = args.add_location
    error = 0
    for filename in args.filenames:
        with tempfile.NamedTemporaryFile() as temp_file:
            with closing(open(filename)) as source_file:
                location = set()
                for line in source_file:
                    if add_location == NEVER:
                        temp_file.write(line.encode())
                        continue

                    if line.startswith(LOCATION_START):
                        location.update(_extract_location_file_name(line))
                    else:
                        for name in sorted(location):
                            temp_file.write(f"{LOCATION_START}{name}\n".encode())
                            error += 1
                        location = set()
                        temp_file.write(line.encode())

            temp_file.seek(0)
            shutil.copyfile(temp_file.name, filename)
    return 1 if error else 0


if __name__ == "__main__":
    exit(main())
