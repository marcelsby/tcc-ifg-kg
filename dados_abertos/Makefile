all: clean collect preprocess

preprocess: clean_preprocess
	@echo Executando o script de pré-processamento
	cd src && python main.py
	@echo Pré-processamento executado com SUCESSO!

clean_preprocess:
	@echo Limpando os arquivos resultantes do pré-processamento...
	(rm -rf data/transformed/*)

collect: clean_collect activate_venv
	@echo Executando o script de coleta...
	cd src && python collect.py
	@echo Arquivos baixados com SUCESSO!

activate_venv:
	@echo Ativando o virtualenv...
	(source ../venv/bin/activate)

clean_collect:
	@echo Limpando os arquivos previamente baixados...
	(rm -rf data/raw/*)

format: activate_venv
	@echo Formatando o código...
	(black src/)
	@echo Código formatado com SUCESSO!

clean: clean_preprocess clean_collect