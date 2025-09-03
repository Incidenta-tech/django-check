#
import os

# Files with logic to start django project
DJANGO_FILES = [
    "wsgi.py",
    "asgi.py",
    "manage.py",
    "settings.py",
]


def get_project_root() -> str:
    """Получает корневую папку проекта."""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.dirname(current_dir)


def get_example_project_path() -> str:
    """Получает путь к тестовому проекту."""
    project_root = get_project_root()
    return os.path.join(project_root, "example")
