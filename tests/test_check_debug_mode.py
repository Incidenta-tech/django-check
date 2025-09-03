from hooks.check_debug_mode import main
from hooks.settings import get_example_project_path

from .utils import TempDjangoProject


def test_debug_mode_without_django():
    assert main([]) == 1


def test_debug_mode_with_project_folder():
    assert main(["--project-folder", "/nonexistent/path"]) == 1


def test_debug_mode_with_test_project():
    test_project_path = get_example_project_path()

    result = main(["--project-folder", test_project_path])
    assert result == 1


def test_debug_mode_with_debug_disabled():
    with TempDjangoProject(custom_settings={"DEBUG": False}) as temp_project_path:
        result = main(["--project-folder", temp_project_path])
        assert result == 0


def test_debug_mode_with_debug_enabled():
    with TempDjangoProject(custom_settings={"DEBUG": True}) as temp_project_path:
        result = main(["--project-folder", temp_project_path])
        assert result == 1


def test_debug_mode_with_debug_not_set():
    with TempDjangoProject() as temp_project_path:
        result = main(["--project-folder", temp_project_path])
        assert result == 1
