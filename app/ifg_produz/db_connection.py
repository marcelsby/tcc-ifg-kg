from app.utils.environment import Environment


def get_ifg_produz_db_connection_url():
    user = Environment.ifg_produz_db_user
    password = Environment.ifg_produz_db_password
    host = Environment.ifg_produz_db_host
    port = Environment.ifg_produz_db_port
    database = Environment.ifg_produz_db_database

    return f"postgresql://{user}:{password}@{host}:{port}/{database}"
