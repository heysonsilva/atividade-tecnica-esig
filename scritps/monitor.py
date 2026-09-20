import subprocess
import time
from datetime import datetime

# iformações que serão usadas ao decorrer do código
url_tomcat  = "http://localhost:8081"
url_wildfly = "http://localhost:8080"
container_tomcat  = "tomcat_app"
container_wildfly = "wildfly_app"

limite_parado = 60

# Controle de tempo parado
tomcat_parado_desde  = None
wildfly_parado_desde = None

while True:
    print("\n=== " + datetime.now().strftime("%H:%M:%S") + " ===")

# tomcat

    resultado = subprocess.run(["curl", "-s", "-o", "NUL", "-w", "%{http_code}", url_tomcat], capture_output=True, text=True)
    codigo = resultado.stdout.strip()

    if codigo != "000" and codigo != "":
        tomcat_parado_desde = None

        info = subprocess.run(
            ["docker", "inspect", "--format={{.State.StartedAt}}", container_tomcat],
            capture_output=True,
            text=True,
        )

        inicio_str = info.stdout.strip()
        inicio = datetime.fromisoformat(inicio_str.replace("Z", "+00:00"))
        agora = datetime.now(inicio.tzinfo)
        diferenca = agora - inicio

        segundos = int(diferenca.total_seconds())
        horas = segundos // 3600
        minutos = (segundos % 3600) // 60
        segs = segundos % 60

        print("[UP]   Tomcat   | HTTP " + codigo + " | uptime: " + str(horas) + "h " + str(minutos) + "m " + str(segs) + "s")

    else:
        if tomcat_parado_desde is None:
            tomcat_parado_desde = time.time()

        tempo_parado = int(time.time() - tomcat_parado_desde)
        print("[DOWN] Tomcat   | parado há " + str(tempo_parado) + "s")

        if tempo_parado >= limite_parado:
            print("       Reiniciando " + container_tomcat + "...")
            subprocess.run(["docker", "restart", container_tomcat], check=True)
            tomcat_parado_desde = None


# wildfly


    resultado = subprocess.run(
        ["curl", "-s", "-o", "NUL", "-w", "%{http_code}", url_wildfly],
        capture_output=True,
        text=True,
    )
    codigo = resultado.stdout.strip()

    if codigo != "000" and codigo != "":
        wildfly_parado_desde = None

        info = subprocess.run(
            ["docker", "inspect", "--format={{.State.StartedAt}}", container_wildfly],
            capture_output=True,
            text=True,
        )
        inicio_str = info.stdout.strip()
        inicio = datetime.fromisoformat(inicio_str.replace("Z", "+00:00"))
        agora = datetime.now(inicio.tzinfo)
        diferenca = agora - inicio

        segundos = int(diferenca.total_seconds())
        horas = segundos // 3600
        minutos = (segundos % 3600) // 60
        segs = segundos % 60

        print("[UP]   WildFly  | HTTP " + codigo + " | uptime: " + str(horas) + "h " + str(minutos) + "m " + str(segs) + "s")

    else:
        if wildfly_parado_desde is None:
            wildfly_parado_desde = time.time()

        tempo_parado = int(time.time() - wildfly_parado_desde)
        print("[DOWN] WildFly  | parado há " + str(tempo_parado) + "s")

        if tempo_parado >= limite_parado:
            print("       Reiniciando " + container_wildfly + "...")
            subprocess.run(["docker", "restart", container_wildfly], check=True)
            wildfly_parado_desde = None

    time.sleep(10)