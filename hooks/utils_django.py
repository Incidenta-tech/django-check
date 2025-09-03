import ast
import os
import sys
import warnings

try:
    from django.conf import Settings

    DJANGO_AVAILABLE = True
except ImportError:
    DJANGO_AVAILABLE = False
    Settings = None

from .settings import DJANGO_FILES
from .utils import get_files_with_extension


def ast_parse(contents_text: str) -> ast.Module:
    # intentionally ignore warnings, we can't do anything about them
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        return ast.parse(contents_text.encode())


def read_file(file_path: str) -> str | None:
    with open(file_path, "rb") as fb:
        contents_bytes = fb.read()

    try:
        return contents_bytes.decode()
    except UnicodeDecodeError:
        print(f"{file_path} is non-utf-8 (not supported)", file=sys.stderr)
        return None


def parse_file(file_content):
    try:
        ast_obj = ast_parse(file_content)
    except SyntaxError:
        return file_content
    else:
        return ast_obj


def extract_django_settings_module(file_content: str) -> str | None:
    """
    Extract DJANGO_SETTINGS_MODULE via AST analysis.

    Args:
        content: File content

    Returns:
        Value of DJANGO_SETTINGS_MODULE or None
    """
    try:
        tree = ast.parse(file_content)

        for node in ast.walk(tree):
            # Looking for os.environ.setdefault("DJANGO_SETTINGS_MODULE", "value")
            if isinstance(node, ast.Call):
                if (
                    isinstance(node.func, ast.Attribute)
                    and isinstance(node.func.value, ast.Attribute)
                    and isinstance(node.func.value.value, ast.Name)
                    and node.func.value.value.id == "os"
                    and node.func.value.attr == "environ"
                    and node.func.attr == "setdefault"
                ):
                    if (
                        len(node.args) >= 2
                        and isinstance(node.args[0], ast.Constant)
                        and node.args[0].value == "DJANGO_SETTINGS_MODULE"
                        and isinstance(node.args[1], ast.Constant)
                    ):
                        return node.args[1].value

            # Looking for os.environ["DJANGO_SETTINGS_MODULE"] = "value"
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if (
                        isinstance(target, ast.Subscript)
                        and isinstance(target.value, ast.Attribute)
                        and isinstance(target.value.value, ast.Name)
                        and target.value.value.id == "os"
                        and target.value.attr == "environ"
                        and isinstance(target.slice, ast.Constant)
                        and target.slice.value == "DJANGO_SETTINGS_MODULE"
                        and isinstance(node.value, ast.Constant)
                    ):
                        return node.value.value

            # Looking for DJANGO_SETTINGS_MODULE = "value"
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if (
                        isinstance(target, ast.Name)
                        and target.id == "DJANGO_SETTINGS_MODULE"
                        and isinstance(node.value, ast.Constant)
                    ):
                        return node.value.value

    except SyntaxError:
        pass

    return None


def init_django_settings(project_folder: str = ".") -> Settings | None:
    """
    Initialize Django settings.

    Returns:
        Settings object or None if Django is not available or settings are not found.
    """
    if not DJANGO_AVAILABLE:
        print("Django is not available")
        return None

    # Looking for file with settings module
    python_files = get_files_with_extension(".py", project_folder)
    priority_files = DJANGO_FILES

    settings_module = None

    for priority_file in priority_files:
        for file_path in python_files:
            if not file_path.endswith(priority_file):
                continue

            # Extract settings module from file
            file_content = read_file(file_path)
            if file_content:
                settings_module = extract_django_settings_module(file_content)
                if settings_module:
                    break
        if settings_module:
            break

    # Configure settings by settings module
    if not settings_module:
        print("Settings module not found")
        return None

    try:
        abs_project_folder = os.path.abspath(project_folder)
        if abs_project_folder not in sys.path:
            sys.path.insert(0, abs_project_folder)

        os.environ.setdefault("DJANGO_SETTINGS_MODULE", settings_module)
        settings = Settings(settings_module)
        return settings
    except Exception as e:
        print(f"Failed to initialize Django settings: {e}")
        return None
