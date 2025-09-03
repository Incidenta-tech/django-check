django-check
================

Some useful hooks for Django development

See also: https://github.com/pre-commit/pre-commit

Inspired by: https://github.com/ecugol/pre-commit-hooks-django

# Using django-check with pre-commit

> django-check works with supported [Django versions](https://www.djangoproject.com/download/?supported-versions) and [Python versions](https://www.python.org/downloads/) only

Add this to your `.pre-commit-config.yaml`

```yaml
-   repo: https://github.com/Incidenta-tech/django-check
    rev: v0.4.0  # Use the ref you want to point at
    hooks:
    -   id: check-untracked-migrations
        # Optional, if specified, hook will work only on these branches
        # otherwise it will work on all branches
        args: ["--branches", "main", "other_branch"]
    -   id: check-unapplied-migrations
    -   id: check-absent-migrations
    -   id: po-location-format
        # Mandatory, select one of the following options:
        # file: show only the file path as location
        # never: remove all locations
        args: ["--add-location", "file"]
```

# Hooks available

## `check-untracked-migrations`

Forbids commit if untracked migrations files are found (e.g. `*/migrations/0001_initial.py`)

### Options:
    --branches

    Optional, if specified, hook will work only on these branches
    otherwise it will work on all branches

## `check-unapplied-migrations`

Check for unapplied migrations with manage.py migrate --check

## `check-absent-migrations`

Check for absent migrations with manage.py makemigrations --check --dry-run

## `po-location-format`

Changes location format for .po files

### Options:

    --add-location [file, never]

    Mandatory, select one of the following options:

    file: show only the file path as location
    never: remove all locations

# Development

> We use poetry as package manager for this package

- `make install` - install dependencies and pre-commit
- `make test` - run tests
- `make check` - run linters and format code
