.PHONY: virtualenv
virtualenv:
	virtualenv -p python3.8 venv

.PHONY: setup
setup:
	pip install -r requirements.txt
	chmod u+x process.py  # to enable -d autocomplete

.PHONY: process
process:
	./process.py
