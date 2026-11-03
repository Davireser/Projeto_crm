# Prompt para criar um backend no mesmo padrão do CRM

Como usar:
1. Abra o Claude Code na pasta raiz do projeto novo.
2. Copie o bloco abaixo e troque só o texto entre `<<< >>>` pela descrição do seu projeto, do jeito que você falaria.
3. A IA monta o domínio a partir da sua descrição, faz perguntas se faltar algo e mostra o plano antes de codar.
4. Para mudar o projeto depois, é só escrever: "Mudança no projeto: ..." (veja o fim do prompt).

```text
Quero que você construa o backend de um projeto da disciplina Laboratório de Programação Web (CEFET-MG). Sou estudante e ainda estou aprendendo Docker e banco de dados, então explique em português simples o que fez em cada etapa.

=== MEU PROJETO ===
<<< Descreva aqui com suas palavras: o que é o sistema, para quem é, que problema resolve, o que o usuário faz nele, quais "coisas" existem (ex.: pacientes, consultas), quais regras não podem ser quebradas, quem pode fazer o quê e que números/relatórios importam. Se tiver enunciado do professor ou pasta docs/, diga onde está. >>>
===================

COMO TRATAR A DESCRIÇÃO
- Leia a descrição (e a documentação, se eu indicar) e extraia: entidades, value objects, a aggregate root, os estados e transições, as regras de negócio, os perfis de usuário e as métricas.
- Use esses nomes em português como linguagem ubíqua em código, banco e docs (nada de Manager, Helper ou nomes genéricos).
- Se faltar informação importante, me faça no máximo 5 perguntas objetivas antes de planejar. No resto, escolha a opção mais sensata e registre como "decisão sujeita a veto".
- O padrão técnico abaixo é fixo; só o domínio muda de projeto para projeto.

O PROFESSOR AVALIA (cubra todos)
1. Introdução e visão geral (estrutura de pastas, dependências)
2. Domínio rico e Clean Architecture
3. Banco de dados e migrations com Alembic
4. Rotas REST e Swagger
5. Autenticação e segurança
6. Qualidade e cobertura de testes (mínimo 80%; mire em 100% de linhas e desvios)
7. Destaques: docker-compose, Dockerfile, escalável, seguro, testado e documentado

STACK
- Python 3.12+, FastAPI, Pydantic v2, pydantic-settings
- SQLAlchemy 2.0 + Alembic + PostgreSQL 17, driver pg8000
- JWT (pyjwt) no login; senha com hash scrypt da biblioteca padrão
- pytest + pytest-cov, ruff, mypy --strict
- Dockerfile e docker-compose

ARQUITETURA (Clean Architecture + DDD), em backend/:
- src/domain: entidades, value objects, regras, exceções, interfaces de repositório. Python puro, sem FastAPI/SQLAlchemy/Pydantic.
- src/application: casos de uso, portas, exceções de aplicação, relógio injetável.
- src/adapters: controllers FastAPI, schemas Pydantic, repositórios PostgreSQL e em memória.
- src/infra: config, models SQLAlchemy, sessão, JWT e hash.
- src/main.py (fábrica do app) e src/criar_administrador.py (CLI do primeiro admin, senha via getpass).
- tests/unit, tests/integration, tests/e2e; alembic/; Dockerfile; pyproject.toml; pytest.ini.
Regras:
- Dependências apontam para dentro. Um teste de arquitetura (escrito primeiro) falha se o domínio importar camadas externas ou frameworks.
- Regras de negócio dentro das entidades e value objects, nunca nos controllers. Estados com tabela de transições como fonte única, exposta numa rota para o frontend.
- Casos de uso recebem repositórios por injeção; repositórios em memória para testar sem banco.
- Erros num formato JSON único com os status certos (400/401/403/404/409/422).
- Datas em UTC; fuso do negócio configurável (FUSO_HORARIO, padrão America/Sao_Paulo).
- Exceções sem sufixo Error (ruff ignora N818).

METODOLOGIA: TDD em partes (teste antes do código; no fim de cada parte, ruff + mypy + pytest verdes)
- Parte 1: estrutura, pyproject, teste de arquitetura, domínio com testes de unidade
- Parte 2: portas, repositórios em memória, casos de uso
- Parte 3: models, repositórios PostgreSQL, migration inicial, testes de integração (contrato, migration, transação, integridade)
- Parte 4: API REST em /api/v1, schemas, erro único, Swagger com tags, testes da API
- Parte 5: login JWT, rota "quem sou eu", usuários só para ADMINISTRADOR, rotas protegidas, JWT_SECRET fraco recusado em produção
- Parte 6: Docker, cobertura obrigatória, README
Antes de codar, crie docs/plano-backend.md (o que será feito, critério de pronto e decisões de cada parte) e me mostre para aprovar. Atualize o plano ao final de cada parte.

TESTES
- pyproject: coverage com source=["src"], branch=true, fail_under=80, show_missing, skip_empty, exclude_also para if __name__ == "__main__":, HTML em htmlcov.
- Integração roda em SQLite por padrão e também em PostgreSQL quando existir TEST_DATABASE_URL (banco só de testes).
- mypy strict em src e tests; ruff com E, F, W, I, N, UP, B, SIM e linha de 100.
- Um teste e2e percorrendo o fluxo principal pela API.

DOCKER
- backend/Dockerfile (python slim), dependências lidas do pyproject.toml via tomllib, PYTHONPATH=/app/src. Alvo "api": usuário sem root, roda alembic upgrade head e depois uvicorn na porta 8000. Alvo "testes": instala o grupo dev e roda pytest --cov.
- docker-compose.yml na raiz:
  - db: postgres:17, porta 127.0.0.1:5432, volume, healthcheck pg_isready -h 127.0.0.1, docker/postgres/init.sql criando o banco de testes
  - api: porta 8000, DATABASE_URL apontando para db, segredos do .env com padrões de desenvolvimento, depends_on service_healthy
  - pgadmin: dpage/pgadmin4 com login (PGADMIN_EMAIL/PGADMIN_PASSWORD do .env), porta 127.0.0.1:5050, servidor já cadastrado via docker/pgadmin/servers.json
  - testes: profiles ["testes"], usa o banco de testes, monta ./backend/htmlcov
- .env.example documentado; .env no .gitignore.

REGRAS DE TRABALHO
- Dependências só no pyproject.toml ([project].dependencies e [dependency-groups].dev). Nunca requirements.txt.
- Nunca mostre segredos do .env; se precisar ler, mascare.
- Uso Windows com PowerShell no VS Code: comandos em sintaxe PowerShell (.\.venv\Scripts\python.exe, $env:VAR = "valor"), sempre dizendo a pasta (raiz ou backend).
- Não faça commit nem push sem eu pedir.
- No fim de cada parte, resumo curto: o que foi feito, nº de testes, cobertura e como testar (Swagger em http://localhost:8000/docs, pgAdmin em http://localhost:5050).

MUDANÇAS DEPOIS
Quando eu escrever "Mudança no projeto: ...", trate como alteração do domínio:
1. Diga o impacto (entidades, regras, rotas, tabelas, testes) e atualize docs/plano-backend.md.
2. Implemente em TDD: ajuste/crie os testes primeiro, depois o código.
3. Crie uma nova migration Alembic se o banco mudar (nunca edite migrations antigas).
4. Rode ruff, mypy e a suíte com cobertura, e me mostre o resultado.

ENTREGA FINAL
Confira o backend contra os 7 itens do professor, dizendo onde cada um está no código, e rode docker compose run --rm testes mostrando o resultado.

Comece lendo minha descrição, faça as perguntas que faltarem e depois escreva o plano para eu aprovar.
```

Exemplos de mudança depois:
- "Mudança no projeto: agora a consulta também pode ser remarcada, no máximo 2 vezes."
- "Mudança no projeto: quero um perfil RECEPCIONISTA que só agenda e não vê relatórios."
- "Mudança no projeto: troque 'Paciente' por 'Cliente' em tudo."
