
pip-tools:
	pip install -U pip
	pip install -U poetry

install-requirements: pip-tools
	poetry install --no-root

install-check:
	poetry run pre-commit install
	poetry run pre-commit install-hooks

install: install-requirements install-check
	echo "Done"

update: pip-tools
	poetry update
	poetry lock
	poetry run pre-commit autoupdate

test:
	poetry run pytest

check:
	poetry run pre-commit run --show-diff-on-failure --color=always --all-files

