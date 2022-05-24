source_venv = . ../venv/bin/activate

all: venv clean collect preprocess

clean: clean_preprocess clean_collect

preprocess: venv clean_preprocess
	@echo Executando o script de pré-processamento
	$(source_venv) && cd src && python main.py
	@echo Pré-processamento executado com SUCESSO!

clean_preprocess:
	@echo Limpando os arquivos resultantes do pré-processamento...
	rm -rf data/transformed/*

collect: venv clean_collect
	@echo Executando o script de coleta...
	$(source_venv) && cd src && python collect.py
	@echo Arquivos baixados com SUCESSO!

clean_collect:
	@echo Limpando os arquivos previamente baixados...
	rm -rf data/raw/*

format: venv
	@echo Formatando o código...
	$(source_venv) && black src/
	@echo Código formatado com SUCESSO!

venv:
	test -d ../venv || (python3 -m venv ../venv && $(source_venv) && pip install -r ../requirements.txt)
