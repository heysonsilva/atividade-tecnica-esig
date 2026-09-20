import subprocess
from datetime import datetime
from pathlib import Path

# Configurações
CONTAINER  = "pg_database"
DB_USER    = "admin"
PASTA_DUMP = Path("dumps")
DB_NAME    = "esig_db"

timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
nome_arquivo = f"{DB_NAME}_{timestamp}.dump"

subprocess.run(["docker", "exec", CONTAINER, "pg_dump", "-U", DB_USER,"-d", DB_NAME, "-Fc", "-f", f"/dumps/{nome_arquivo}"],
               check=True,)

arquivo = PASTA_DUMP / nome_arquivo

print(f"Dump criado em: {arquivo}")
