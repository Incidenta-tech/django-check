import os
import subprocess
import sys

import pytest


@pytest.fixture(autouse=True)
def clean_django_state():
    def forget_test_project():
        modules_to_remove = [key for key in sys.modules.keys() if key.startswith("testproject")]
        for module in modules_to_remove:
            del sys.modules[module]

    original_django_settings_module = os.environ.get("DJANGO_SETTINGS_MODULE")
    original_sys_path = sys.path.copy()
    forget_test_project()
    yield

    if original_django_settings_module:
        os.environ["DJANGO_SETTINGS_MODULE"] = original_django_settings_module
    elif "DJANGO_SETTINGS_MODULE" in os.environ:
        del os.environ["DJANGO_SETTINGS_MODULE"]

    sys.path[:] = original_sys_path
    forget_test_project()


@pytest.fixture
def temp_git_dir(tmpdir):
    git_dir = tmpdir.join("gits")
    subprocess.call(["git", "init", "--", str(git_dir)])
    yield git_dir
