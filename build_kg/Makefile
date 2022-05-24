source_venv = . ../venv/bin/activate

all: venv

format: venv
	@echo Formatando o código...
	$(source_venv) && black .
	@echo Código formatado com SUCESSO!

venv:
	test -d ../venv || (python3 -m venv ../venv && $(source_venv) && pip install -r ../requirements.txt)
