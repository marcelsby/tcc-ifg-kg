from app.build_kg.main import execute as build_kg
from app.dados_abertos.main import execute as process_dados_abertos
from app.ifg_produz.main import execute as process_ifg_produz

if __name__ == '__main__':
    process_dados_abertos()
    process_ifg_produz()

    build_kg()
