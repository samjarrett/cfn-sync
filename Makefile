FILES := cfn_sync tests setup.py

lint:
	pylint ${FILES}
	black --check ${FILES}
	isort --recursive ${FILES} --check-only

test:
	pytest --cov cfn_sync
	mypy cfn_sync

fix:
	black ${FILES}
	isort --recursive ${FILES}
	$(MAKE) lint
