# Atividade Técnica — Estágio Infraestrutura (ESIG Group)

Atividade prática de **dump/restore de PostgreSQL** e **monitoramento de serviços Java** (Tomcat e WildFly) em containers Docker.

---

## 📁 Estrutura do projeto

```
.
├── apps/
│   ├── tomcat/
│   │   └── index.html                  # página servida pelo Tomcat
│   └── wildfly/
│   │   ├── ROOT.war/
│   │   │   └── index.html              # página servida pelo WildFly
│   └── ROOT.war.dodeploy           # marcador de deploy do WildFly
├── dumps/                              # arquivos de dump gerados
├── postgres/
│   └── init/
│       └── init.sql                    # cria tabela + dados de exemplo
├── scripts/
│   ├── dump_db.py                      # gera dump do banco
│   ├── restore_db.py                   # restaura o último dump
│   └── monitor.py                      # monitora Tomcat e WildFly
├── compose.yaml
└── README.md
```

---

## 🛠️ Pré-requisitos

- **Docker Desktop** instalado e rodando
- **Python 3** instalado

Verifique:

```bash
docker --version
docker compose version
python --version
```

---

## Diagrama de Funcionamento

<img width="1701" height="974" alt="deepseek_mermaid_20260920_9ea0c6" src="https://github.com/user-attachments/assets/571ac038-3093-4ba8-860b-8f77d01b3c4d" />


---

## 🚀 Como executar

### 1. Subir os serviços

Na raiz do projeto:

```bash
docker compose up -d
```

Isso sobe três containers:

| Serviço | Container | Porta (host) |
|---|---|---|
| PostgreSQL | `pg_database` | 5432 |
| Tomcat | `tomcat_app` | 8081 |
| WildFly | `wildfly_app` | 8080 / 9990 |

### 2. Testar os serviços

```bash
curl http://localhost:8081     # Tomcat → HTML
curl http://localhost:8080     # WildFly → HTML
```

### 3. Gerar um dump do banco

```bash
cd scripts
python dump_db.py
```

O arquivo é salvo em `dumps/` com timestamp no nome.

### 4. Restaurar o último dump

```bash
python restore_db.py
```

### 5. Monitorar Tomcat e WildFly

```bash
python monitor.py
```

O script verifica os endpoints a cada 10 segundos e reinicia o container se o serviço ficar fora do ar por mais de 60 segundos.
