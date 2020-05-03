lint:
	pylint cfn_sync tests setup.py
	black -c cfn_sync tests setup.py

test:
	pytest --cov cfn_sync
	mypy cfn_sync
