import subprocess
from pathlib import Path

# Configurações
CONTAINER  = "pg_database"
DB_USER    = "admin"
DB_NAME    = "esig_db"
PASTA_DUMP = Path(__file__).parent.parent / "dumps"

dumps = sorted(PASTA_DUMP.glob("*.dump"))
ultimo_dump = dumps[-1]

#  recria  o banco de dados
query = (f"SELECT pg_terminate_backend(pid) FROM pg_stat_activity " f"WHERE datname = '{DB_NAME}' AND pid <> pg_backend_pid();")

subprocess.run(["docker", "exec", CONTAINER, "psql", "-U", DB_USER, "-d", "postgres", "-c", query], check=True,)

subprocess.run(["docker", "exec", CONTAINER, "psql", "-U", DB_USER, "-d", "postgres", "-c",
                f"DROP DATABASE IF EXISTS {DB_NAME};"], check=True,)

subprocess.run(["docker", "exec", CONTAINER,"psql", "-U", DB_USER, "-d", "postgres", "-c",
                f"CREATE DATABASE {DB_NAME};"], check=True,)

subprocess.run(["docker", "exec", CONTAINER,"pg_restore", "-U", DB_USER, "-d", DB_NAME, f"/dumps/{ultimo_dump.name}"],check=True,)

print(f"Restore concluído a partir de: {ultimo_dump.name}")