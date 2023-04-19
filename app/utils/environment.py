from os import getenv


class Environment:
    neo4j_host: str = getenv("NEO4J_HOST") or "localhost"
    neo4j_port: int = int(getenv("NEO4J_PORT")) or 7687

    neo4j_user: str = getenv("NEO4J_USER")
    neo4j_password: str = getenv("NEO4J_PASSWORD")
