"""
# Simple usage without changing settings
with TempDjangoProject() as project_path:
    # Work with temporary project
    pass

# With settings
settings = {'DEBUG': False, 'ALLOWED_HOSTS': ['*'], 'TIME_ZONE': 'Europe/Moscow'}
with TempDjangoProject(custom_settings=settings) as project_path:
    # Work with configured project
    pass

# With specific setting DEBUG
with TempDjangoProject(custom_settings={'DEBUG': False}) as project_path:
    # Work with project where DEBUG = False
    pass
"""

import os
import shutil
import tempfile
from typing import Any

from hooks.settings import get_example_project_path


class TempDjangoProject:
    """Context manager for creating a temporary Django project."""

    def __init__(self, custom_settings: dict[str, Any] | None = None):
        self.custom_settings = custom_settings
        self.project_path: str | None = None

    def __enter__(self) -> str:
        self.project_path = self._create_temp_project()
        return self.project_path

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.project_path:
            self._cleanup_project()

    def _create_temp_project(self) -> str:
        """
        Creates a temporary Django project for testing.

        Returns:
            Path to the temporary project
        """
        temp_dir = tempfile.mkdtemp()
        example_path = get_example_project_path()

        # Copy all example folder to temporary directory
        temp_project_path = os.path.join(temp_dir, "example")
        shutil.copytree(example_path, temp_project_path)

        # Update settings.py
        self._update_settings_file(temp_project_path)

        return temp_project_path

    def _update_settings_file(self, project_path: str) -> None:
        """
        Updates the settings.py file in the temporary project.

        Args:
            project_path: Path to the project
        """
        settings_path = os.path.join(project_path, "testproject", "settings.py")

        with open(settings_path, encoding="utf-8") as f:
            content = f.read()

        # Apply settings
        if self.custom_settings:
            content = self._apply_custom_settings(content, self.custom_settings)

        with open(settings_path, "w", encoding="utf-8") as f:
            f.write(content)

    def _apply_custom_settings(self, content: str, settings: dict[str, Any]) -> str:
        """
        Applies additional settings to the settings.py content.

        Args:
            content: Content of the settings.py file
            settings: Dictionary with settings

        Returns:
            Updated content of the file
        """
        lines = content.split("\n")

        for setting_name, setting_value in settings.items():
            # Looking for existing setting
            setting_found = False
            for i, line in enumerate(lines):
                if line.strip().startswith(f"{setting_name} ="):
                    # Found setting, need to replace it and delete all related lines
                    new_setting = f"{setting_name} = {self._format_setting_value(setting_value)}"

                    # Define range of lines to delete (multiline settings)
                    start_index = i
                    end_index = i

                    # If setting contains opening bracket, looking for closing bracket
                    if any(bracket in line for bracket in ["{", "[", "("]):
                        bracket_count = 0
                        for bracket in line:
                            if bracket in "{[(":
                                bracket_count += 1
                            elif bracket in "}])":
                                bracket_count -= 1

                        # Looking for closing brackets in the next lines
                        j = i + 1
                        while j < len(lines) and bracket_count > 0:
                            for bracket in lines[j]:
                                if bracket in "{[(":
                                    bracket_count += 1
                                elif bracket in "}])":
                                    bracket_count -= 1
                            if bracket_count > 0:
                                j += 1
                            else:
                                end_index = j
                                break
                        else:
                            end_index = j - 1 if j > i + 1 else i

                    # Replace range of lines with one new setting
                    if isinstance(setting_value, (dict, list)) and len(setting_value) > 0:
                        # For complex settings use multiline format
                        new_lines = new_setting.split("\n")
                        lines[start_index : end_index + 1] = new_lines
                    else:
                        # For simple settings use singleline format
                        lines[start_index : end_index + 1] = [new_setting]

                    setting_found = True
                    break

            # If setting not found, add it to the end of the file
            if not setting_found:
                lines.append(f"{setting_name} = {self._format_setting_value(setting_value)}")

        return "\n".join(lines)

    def _format_setting_value(self, value: Any, indent_level: int = 0) -> str:
        """
        Formats the setting value for writing to settings.py.

        Args:
            value: Setting value
            indent_level: Indent level for formatting

        Returns:
            Formatted string
        """
        if isinstance(value, str):
            return f'"{value}"'
        elif isinstance(value, bool):
            return str(value)
        elif isinstance(value, (int, float)):
            return str(value)
        elif isinstance(value, (list, tuple)):
            if not value:
                bracket_type = "[" if isinstance(value, list) else "("
                closing_bracket = "]" if isinstance(value, list) else ")"
                return f"{bracket_type}{closing_bracket}"

            formatted_items = [self._format_setting_value(item, indent_level + 1) for item in value]
            bracket_type = "[" if isinstance(value, list) else "("
            closing_bracket = "]" if isinstance(value, list) else ")"

            # For simple lists use singleline format
            if all(isinstance(item, (str, int, float, bool)) for item in value):
                return f"{bracket_type}{', '.join(formatted_items)}{closing_bracket}"
            else:
                # For complex lists use multiline format
                indent = "    " * (indent_level + 1)
                items_str = f",\n{indent}".join(formatted_items)
                return f"{bracket_type}\n{indent}{items_str}\n{'    ' * indent_level}{closing_bracket}"
        elif isinstance(value, dict):
            if not value:
                return "{}"

            formatted_items = []
            for k, v in value.items():
                formatted_value = self._format_setting_value(v, indent_level + 1)
                formatted_items.append(f'"{k}": {formatted_value}')

            # For simple dictionaries use singleline format
            if all(isinstance(v, (str, int, float, bool)) for v in value.values()) and len(value) <= 3:
                return f"{{{', '.join(formatted_items)}}}"
            else:
                # For complex dictionaries use multiline format
                indent = "    " * (indent_level + 1)
                items_str = f",\n{indent}".join(formatted_items)
                return f"{{\n{indent}{items_str}\n{'    ' * indent_level}}}"
        else:
            return repr(value)

    def _cleanup_project(self) -> None:
        """Deletes the temporary project."""
        if self.project_path:
            # Get parent folder (temp_dir)
            temp_dir = os.path.dirname(self.project_path)
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)

    def get_settings(self) -> dict[str, Any]:
        """
        Gets settings from the temporary project.

        Returns:
            Dictionary with settings from settings.py

        Raises:
            RuntimeError: If project is not created
        """
        if not self.project_path:
            raise RuntimeError("Project is not created. Use context manager or create project.")

        import importlib.util
        import sys

        # Add project path to sys.path
        if self.project_path not in sys.path:
            sys.path.insert(0, self.project_path)

        try:
            # Import settings
            settings_path = os.path.join(self.project_path, "testproject", "settings.py")
            spec = importlib.util.spec_from_file_location("settings", settings_path)
            settings_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(settings_module)

            # Get main settings
            result = {}
            for attr_name in dir(settings_module):
                if not attr_name.startswith("_"):
                    result[attr_name] = getattr(settings_module, attr_name)

            return result
        finally:
            # Remove path from sys.path
            if self.project_path in sys.path:
                sys.path.remove(self.project_path)
