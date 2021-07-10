FILES := cfn_sync tests setup.py

lint:
	pylint ${FILES}
	black --check ${FILES}
	isort ${FILES} --check-only

test:
	pytest --cov cfn_sync --cov-report html --cov-report term
	mypy cfn_sync

fix:
	black ${FILES}
	isort ${FILES}
	$(MAKE) lint
