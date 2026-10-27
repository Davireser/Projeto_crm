# Prompt para criar um backend no mesmo padrão do CRM

Como usar:
1. Preencha os campos entre `[colchetes]` da seção "MEU PROJETO".
2. Se tiver o enunciado do professor ou uma pasta `docs/` com requisitos, coloque junto (ou diga onde está).
3. Abra o Claude Code **na pasta raiz do projeto novo** e cole tudo a partir da linha "INÍCIO DO PROMPT".
4. Ele vai planejar e pedir aprovação antes de cada parte. Responda "pode seguir" ou peça ajustes.

---

INÍCIO DO PROMPT

Quero que você construa o backend do meu projeto da disciplina Laboratório de Programação Web (CEFET-MG), seguindo exatamente o padrão descrito abaixo. Sou estudante e ainda estou aprendendo Docker e banco de dados, então explique em português simples o que você fez em cada etapa.

## MEU PROJETO

- **Nome do produto:** [ex.: Sistema de Agendamento de Consultas]
- **Domínio / para quem é:** [ex.: clínicas pequenas que hoje agendam por WhatsApp e caderno]
- **Problema que resolve:** [1 ou 2 frases]
- **Entidades principais (linguagem ubíqua):** [ex.: Paciente, Consulta, Profissional, Horario]
- **Aggregate root:** [a entidade central que protege as regras, ex.: Consulta]
- **Regras de negócio importantes:** [ex.: consulta passa por AGENDADA → CONFIRMADA → REALIZADA ou CANCELADA; não pode marcar dois pacientes no mesmo horário; só cancela com 24h de antecedência]
- **Perfis de usuário:** [ex.: USUARIO e ADMINISTRADOR]
- **Métricas/relatórios desejados:** [ex.: taxa de comparecimento, consultas por profissional]
- **Requisitos/documentação existente:** [ex.: pasta docs/ com requisitos e diagramas, ou "não tenho, crie a partir desta descrição"]
- **Fora de escopo:** [o que NÃO precisa fazer]

## O QUE O PROFESSOR VAI AVALIAR (o backend tem que cobrir tudo)

1. Introdução e visão geral do projeto (estrutura de pastas, dependências).
2. Domínio rico e Clean Architecture.
3. Banco de dados e migrations com Alembic.
4. Rotas REST e documentação Swagger.
5. Autenticação e segurança.
6. Qualidade e cobertura de testes (meta mínima de 80%; mire em 100% de linhas e desvios).
7. Destaques: docker-compose, Dockerfile, projeto escalável, seguro, testado e documentado.

## STACK OBRIGATÓRIA

- Python 3.12+ com **FastAPI**, **Pydantic v2** e **pydantic-settings**.
- **SQLAlchemy 2.0** + **Alembic** + PostgreSQL 17. Driver **pg8000** (Python puro).
- **JWT** (pyjwt) para login; senhas com hash **scrypt** da biblioteca padrão (`hashlib.scrypt`), nunca em texto puro.
- Testes com **pytest** + **pytest-cov**; lint com **ruff**; tipos com **mypy --strict**.
- **Docker**: `Dockerfile` do backend e `docker-compose.yml` na raiz.

## ARQUITETURA (Clean Architecture + DDD)

Estrutura em `backend/`:

```
backend/
├── src/
│   ├── domain/          # entidades, value objects, regras, exceções, interfaces de repositório. Python puro.
│   ├── application/     # casos de uso, portas (interfaces), exceções de aplicação, relógio
│   ├── adapters/        # controllers FastAPI, schemas Pydantic, repositórios (Postgres e em memória)
│   ├── infra/           # config, banco (models SQLAlchemy, sessão), segurança (JWT, hash)
│   ├── main.py          # cria o app FastAPI (fábrica)
│   └── criar_administrador.py  # CLI para criar o primeiro admin
├── tests/
│   ├── unit/            # domínio, casos de uso, teste de arquitetura
│   ├── integration/     # API, repositórios, migrations, transações (SQLite e PostgreSQL)
│   └── e2e/             # um fluxo completo pela API
├── alembic/  alembic.ini
├── Dockerfile  .dockerignore
├── pyproject.toml  pytest.ini
```

Regras:
- **Dependências apontam para dentro**: domain não importa nada de application/adapters/infra, nem FastAPI, SQLAlchemy ou Pydantic. Crie um **teste de arquitetura** (`tests/unit/test_arquitetura.py`) que falha se isso for violado. Escreva esse teste primeiro.
- **Domínio rico**: as regras ficam nas entidades e value objects (validação de e-mail, telefone, valores, transições de estado), não nos controllers. Use enums com tabela de transições permitidas como fonte única de verdade, e exponha essas transições numa rota para o frontend.
- **Linguagem ubíqua em português** em código, banco e docs (nomes de classes, exceções, tabelas). Nada de nomes genéricos como `Manager` ou `Helper`. Exceções sem sufixo `Error` (configure o ruff para ignorar N818).
- Casos de uso recebem repositórios por **injeção de dependência** (portas). Ter repositórios **em memória** para testar casos de uso sem banco.
- **Erros num formato JSON único** em toda a API (código, mensagem, detalhes), com os status HTTP corretos (400/401/403/404/409/422).
- Datas em UTC no banco; fuso do negócio configurável (`FUSO_HORARIO`, padrão `America/Sao_Paulo`).

## METODOLOGIA (TDD, em partes)

Trabalhe em **partes incrementais**, e em cada uma: escreva os testes antes do código (vermelho → verde → refatorar), rode ruff, mypy e pytest no fim e só passe para a próxima com tudo verde.

- **Parte 1, Fundação + Domínio:** estrutura, pyproject, teste de arquitetura, entidades, value objects e regras com testes de unidade.
- **Parte 2, Casos de uso:** portas, repositórios em memória e casos de uso com testes.
- **Parte 3, Persistência:** models SQLAlchemy, repositórios PostgreSQL, migration inicial no Alembic, testes de integração (contrato dos repositórios, migrations, transações, integridade).
- **Parte 4, API REST:** controllers FastAPI (base `/api/v1`), schemas, formato único de erro, Swagger organizado por tags, testes da API.
- **Parte 5, Autenticação e usuários:** login JWT, rota "quem sou eu", CRUD de usuários só para ADMINISTRADOR, todas as rotas protegidas, CLI `criar_administrador.py` (senha via getpass), `JWT_SECRET` fraco recusado em produção.
- **Parte 6, Docker e cobertura:** Dockerfile, docker-compose, cobertura ≥ 80% obrigatória (mire em 100%), README atualizado.

Antes de começar, crie `docs/plano-backend.md` com o plano de todas as partes (o que será feito, critério de pronto e decisões de projeto) e **me mostre para aprovar**. Atualize esse plano ao final de cada parte.

## TESTES E QUALIDADE

- No `pyproject.toml`: `[tool.coverage.run]` com `source = ["src"]` e `branch = true`; `[tool.coverage.report]` com `fail_under = 80`, `show_missing = true`, `skip_empty = true` e `exclude_also = ['if __name__ == "__main__":']`; relatório HTML em `htmlcov`.
- Testes de integração rodam em SQLite por padrão; quando a variável `TEST_DATABASE_URL` existir, rodam também no PostgreSQL (banco separado só para testes, que pode ser apagado).
- `mypy` em modo strict cobrindo `src` e `tests`; `ruff` com as regras E, F, W, I, N, UP, B e SIM e linha de 100 caracteres.
- Inclua um teste e2e que percorre o fluxo principal inteiro pela API.

## DOCKER

- `backend/Dockerfile` com base `python:3.x-slim`, instalando as dependências **lidas do pyproject.toml** (via tomllib) e `PYTHONPATH=/app/src`. Dois alvos:
  - `api`: usuário sem root; ao iniciar roda `alembic upgrade head` e depois `uvicorn main:app --host 0.0.0.0 --port 8000`.
  - `testes`: instala o grupo dev e roda `pytest --cov`.
- `docker-compose.yml` na raiz com 4 serviços:
  - `db`: postgres:17, senha via `${POSTGRES_PASSWORD:-...}`, porta só em `127.0.0.1:5432`, volume persistente, healthcheck com `pg_isready -h 127.0.0.1`, e um `docker/postgres/init.sql` que cria o banco de testes.
  - `api`: porta 8000, `DATABASE_URL` apontando para `db`, segredos vindos do `.env` com padrões de desenvolvimento, `depends_on` com `condition: service_healthy`.
  - `pgadmin`: `dpage/pgadmin4` com tela de login (`PGADMIN_EMAIL`/`PGADMIN_PASSWORD` do `.env`), porta `127.0.0.1:5050`, servidor do banco já cadastrado via `docker/pgadmin/servers.json`.
  - `testes`: com `profiles: ["testes"]` (só roda com `docker compose run --rm testes`), usando o banco de testes e montando `./backend/htmlcov`.
- `.env.example` documentado na raiz; o `.env` real fica no `.gitignore`.

## REGRAS DE TRABALHO (importantes)

- **Dependências só no `pyproject.toml`** (`[project].dependencies` e `[dependency-groups].dev`). Nunca crie `requirements.txt`.
- **Nunca mostre segredos do `.env`** no chat; se precisar ler, mascare os valores.
- Eu uso **Windows com PowerShell no VS Code**. Todo comando que eu precisar rodar deve vir em sintaxe PowerShell (`.\.venv\Scripts\python.exe`, `$env:VAR = "valor"`), dizendo **em qual pasta** rodar (raiz do projeto ou `backend`).
- Não faça commit sem eu pedir. Quando eu pedir, faça commits pequenos por parte.
- Se uma decisão de projeto for ambígua, proponha a opção recomendada e siga, registrando no plano como "sujeita a veto".
- Ao final de cada parte, me dê um resumo curto: o que foi feito, quantos testes, cobertura, e como eu testo (comandos e endereços: Swagger em http://localhost:8000/docs, pgAdmin em http://localhost:5050).

## ENTREGA FINAL

Quando tudo estiver pronto, confira o backend contra os 7 itens que o professor avalia e me diga, item por item, onde cada um está atendido no código. Depois, rode a suíte dentro do Docker (`docker compose run --rm testes`) e me mostre o resultado.

Comece lendo a documentação que eu indiquei acima, depois escreva o `docs/plano-backend.md` e me mostre antes de codar.

FIM DO PROMPT
