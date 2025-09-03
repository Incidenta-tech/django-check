import argparse
from collections.abc import Sequence

from .utils_django import init_django_settings


def check_debug_mode_via_django_settings(project_folder: str = ".") -> bool:
    """
    Check DEBUG mode via Django settings.

    Args:
        project_folder: Path to the project folder.

    Returns:
        True if DEBUG = False, False if DEBUG = True or an error occurred.
    """
    try:
        settings = init_django_settings(project_folder)
        if settings is None:
            print("ERROR: Django settings are not initialized")
            return False

        # Get DEBUG value from Django settings
        settings_value = getattr(settings, "DEBUG", None)
        print(f"DEBUG mode: {settings_value}")
        return settings_value is False
    except Exception:
        print("ERROR: Failed to check DEBUG mode")
        return False


def main(argv: Sequence[str] | None = None) -> int:
    """Main function for checking DEBUG mode."""
    parser = argparse.ArgumentParser(description="Check that DEBUG mode is disabled in Django settings")
    parser.add_argument("filenames", nargs="*", help="Files to check (if not specified, search automatically)")
    parser.add_argument("--project-folder", default=".", help="Project folder path")

    args = parser.parse_args(argv)

    is_debug_disabled = check_debug_mode_via_django_settings(args.project_folder)

    if not is_debug_disabled:
        print("ERROR: DEBUG mode is not disabled in Django settings")
        return 1
    else:
        print("OK: DEBUG is correctly disabled in Django settings")
        return 0


if __name__ == "__main__":
    exit(main())
