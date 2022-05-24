source_venv = . ../venv/bin/activate

all: clean collect preprocess

preprocess: clean_preprocess
	@echo Executando o script de pré-processamento
	$(source_venv) && cd src && python main.py
	@echo Pré-processamento executado com SUCESSO!

clean_preprocess:
	@echo Limpando os arquivos resultantes do pré-processamento...
	rm -rf data/transformed/*

collect: clean_collect
	@echo Executando o script de coleta...
	$(source_venv) && cd src && python collect.py
	@echo Arquivos baixados com SUCESSO!

clean_collect:
	@echo Limpando os arquivos previamente baixados...
	rm -rf data/raw/*

format: 
	@echo Formatando o código...
	$(source_venv) && black src/
	@echo Código formatado com SUCESSO!

clean: clean_preprocess clean_collect
