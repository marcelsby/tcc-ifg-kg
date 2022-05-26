source_venv = . ../venv/bin/activate

all: venv insert

insert: test
	$(source_venv) && python3 main.py

test:
	$(source_venv) && python3 tests.py -v

format: venv
	@echo Formatando o código...
	$(source_venv) && black .

venv:
	test -d ../venv || (python3 -m venv ../venv && $(source_venv) && pip install -r ../requirements.txt)
