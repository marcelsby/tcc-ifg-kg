collect: clean_collect activate_venv
	@echo Executando o script de coleta...
	cd src && python collect.py
	@echo Arquivos baixados com sucesso!

activate_venv:
	@echo Ativando o virtualenv...
	(source ../venv/bin/activate)

clean_collect:
	@echo Limpando os arquivos previamente baixados...
	(rm -rf data/raw/*)