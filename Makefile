FILES := cfn_sync tests setup.py

lint:
	uv run pylint ${FILES}
	uv run black --check ${FILES}
	uv run isort ${FILES} --check-only

test:
	uv run pytest --cov cfn_sync --cov-report html --cov-report term
	uv run mypy cfn_sync

fix:
	uv run black ${FILES}
	uv run isort ${FILES}
	$(MAKE) lint
