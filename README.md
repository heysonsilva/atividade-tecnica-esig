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

---

## 🗄️ PostgreSQL — Dump e Restore

### Banco de exemplo

O banco `esig_db` é criado automaticamente pela variável `POSTGRES_DB` no compose. A tabela `clientes` é populada pelo `init.sql` na primeira subida do container.

```sql
CREATE TABLE IF NOT EXISTS clientes (
    id        SERIAL PRIMARY KEY,
    nome      VARCHAR(100) NOT NULL,
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Como funciona o dump

O script `dump_db.py` executa `pg_dump` **dentro do container** via `docker exec`:

```bash
docker exec pg_database pg_dump -U admin -d esig_db -Fc -f /dumps/<arquivo>.dump
```

**Decisões técnicas:**

| Item | Escolha | Motivo |
|---|---|---|
| Formato | `-Fc` (custom) | Comprimido e compatível com `pg_restore` |
| Execução | `docker exec` | Não exige cliente Postgres no host |
| Saída | Pasta `/dumps` (bind mount) | Arquivo aparece no host automaticamente |
| Nome | Timestamp | Ordenação alfabética = cronológica |

### Como funciona o restore

O script `restore_db.py`:

1. Localiza o **dump mais recente** em `dumps/`
2. **Mata conexões ativas** no banco (senão o `DROP DATABASE` falha)
3. **Dropa e recria** o banco
4. Executa `pg_restore` do dump

Cada passo é um `docker exec` separado, porque o `DROP DATABASE` **não pode rodar dentro de uma transação**.

---

## 🐱🐘 Tomcat e WildFly — Monitoramento

### Como funciona

O script `monitor.py`:

1. Faz um `curl` em cada endpoint a cada 10 segundos
2. Considera **UP** se o servidor responde **qualquer código HTTP** (200, 403, 404 etc.)
3. Considera **DOWN** se a conexão falha (código `000`)
4. Obtém o **uptime** via `docker inspect`
5. Se um serviço ficar DOWN por **mais de 60 segundos**, reinicia o container via `docker restart`

### Por que 404 é considerado UP

O objetivo é monitorar **disponibilidade do servidor**, não da aplicação. Um 404 significa que o servidor **está no ar**, mas não tem conteúdo naquele caminho. Se estivesse fora, retornaria `000` (conexão falha).

### Decisões técnicas

| Item | Escolha | Motivo |
|---|---|---|
| Detecção | `curl` HTTP | Reflete se o serviço responde |
| Uptime | `docker inspect` | Fonte confiável de metadados do container |
| Ação | `docker restart` | Reinicia o container se o serviço cair |
| Loop | `while True` + `sleep` | Monitoramento contínuo |

---

## 🐳 Decisões de infraestrutura

### Por que Docker

- **Reprodutibilidade**: qualquer pessoa roda `docker compose up` e tem o ambiente
- **Isolamento**: cada serviço em seu próprio container
- **Portabilidade**: funciona igual em Windows, Linux e Mac

### WildFly — configuração necessária

O WildFly, por padrão, escuta apenas em `127.0.0.1`. Para aceitar conexões externas ao container, foi necessário passar:

```bash
-b 0.0.0.0 -bmanagement 0.0.0.0
```

Sem isso, o Docker mapeia a porta, mas o WildFly recusa conexões do host.

### WildFly — deploy de pasta `.war`

O WildFly exige um **arquivo marcador** `.dodeploy` ao lado de uma pasta `.war` para fazer deploy automático. O marcador é consumido e **apagado** após o deploy.

Como o marcador estava montado via **bind mount**, o WildFly não conseguia apagá-lo — e entrava em **loop infinito de redeploy**.

**Solução:** o `.dodeploy` é montado em `/tmp/` e **copiado** para `deployments/` no `command` do compose, antes de subir o WildFly. Assim, o arquivo fica na camada de escrita do container e pode ser apagado normalmente.

### Estrutura do Tomcat vs. WildFly

- **Tomcat**: o `index.html` fica em `apps/tomcat/`, montado em `webapps/ROOT/`. O Tomcat serve a pasta diretamente.
- **WildFly**: o `index.html` fica dentro de `apps/wildfly/ROOT.war/`, montado em `deployments/ROOT.war`. O `.dodeploy` fica em `apps/wildfly/`.

---

## 🧰 Tecnologias utilizadas

- **Docker / Docker Compose**
- **PostgreSQL 16**
- **Tomcat 10.1 (JDK 17)**
- **WildFly 41**
- **Python 3** (`subprocess`, `pathlib`, `datetime`)

---

## ⚠️ Observações

- O `init.sql` roda **apenas na primeira subida** do container, quando o banco está vazio.
- Para recriar o banco do zero:
  ```bash
  docker compose down
  docker compose up -d
  ```
- O script `monitor.py` roda em **loop infinito**. Para parar, use `Ctrl+C`.
- No Windows, o `curl` usa `NUL` como "buraco negro". Em Linux, seria `/dev/null`.

---

## 📚 Referências

- [Documentação oficial do PostgreSQL — pg_dump](https://www.postgresql.org/docs/current/app-pgdump.html)
- [Documentação oficial do PostgreSQL — pg_restore](https://www.postgresql.org/docs/current/app-pgrestore.html)
- [Documentação do WildFly](https://docs.wildfly.org/)
- [Documentação do Tomcat](https://tomcat.apache.org/tomcat-10.1-doc/)
