import os
import subprocess

UNTRACKED_CMD = ["git", "ls-files", "--others", "--exclude-standard"]
BRANCH_CMD = ["git", "symbolic-ref", "--short", "HEAD"]


def get_untracked_files() -> list[str]:
    output = subprocess.check_output(UNTRACKED_CMD)
    return output.decode().split("\n")


def get_current_branch() -> str:
    output = subprocess.check_output(BRANCH_CMD)
    return output.decode().rstrip()


def get_files_with_extension(
    extension: str,
    root_path: str = ".",
    exclude_dirs: list[str] | None = None,
) -> list[str]:
    """
    Recursively finds all files with the specified extension, excluding specified directories.

    Args:
        extension: File extension (e.g., ".py", ".txt", ".json")
        root_path: Root directory for search (default is current)
        exclude_dirs: List of directories to exclude

    Returns:
        List of paths to files with the specified extension
    """
    if exclude_dirs is None:
        exclude_dirs = [
            "venv",
            "__pycache__",
            "node_modules",
            "build",
            "dist",
            "migrations",
            "media",
            "static",
            "staticfiles",
            "templates",
            "deactivate",
        ]

    found_files = []

    for root, dirs, files in os.walk(root_path):
        dirs[:] = [d for d in dirs if d not in exclude_dirs and not d.startswith(".")]

        for file in files:
            if file.endswith(extension):
                file_path = os.path.join(root, file)
                found_files.append(file_path)

    return found_files
