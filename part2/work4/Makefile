DEFAULT_PYTHONPATH := ./src
PYTHON := venv/bin/python


install-dev:
	python3 -m venv venv

run-server:
	PYTHONPATH=$(DEFAULT_PYTHONPATH) $(PYTHON) ./src/server/main.py

run-client:
	PYTHONPATH=$(DEFAULT_PYTHONPATH) $(PYTHON) ./src/client/main.py

tests:
	PYTHONPATH=. pytest -vv
