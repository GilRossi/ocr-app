PYTHON ?= python3
VENV_DIR ?= .venv
VENV_PYTHON := $(VENV_DIR)/bin/python
VENV_PIP := $(VENV_DIR)/bin/pip

.PHONY: setup run test learn graph

setup:
	$(PYTHON) -m venv $(VENV_DIR)
	$(VENV_PIP) install -r requirements.txt

run:
	$(VENV_PYTHON) -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload

test:
	$(VENV_PYTHON) -m unittest discover -s tests

learn:
	$(VENV_PYTHON) -m parser.learn_parser

graph:
	$(VENV_PYTHON) scripts/grafico_aprendizado.py
