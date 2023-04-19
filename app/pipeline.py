from app.build_kg.main import execute as build_kg
from app.dados_abertos.main import execute as process_dados_abertos

if __name__ == '__main__':
    process_dados_abertos()
    build_kg()
