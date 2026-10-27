# Imagem do backend (RNF09). Quem monta e sobe é o docker-compose.yml da raiz do projeto.
# Dois alvos: "api" (servidor, o padrão) e "testes" (suíte com cobertura).

FROM python:3.14-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PYTHONPATH=/app/src

WORKDIR /app

# Dependências antes do código: esta camada só é refeita quando o pyproject.toml muda.
# A lista sai do próprio pyproject.toml, que continua sendo a única fonte.
COPY pyproject.toml .
RUN python -c "import tomllib; print('\n'.join(tomllib.load(open('pyproject.toml', 'rb'))['project']['dependencies']))" > /tmp/dependencias.txt \
    && pip install -r /tmp/dependencias.txt \
    && rm /tmp/dependencias.txt

COPY alembic.ini .
COPY alembic ./alembic
COPY src ./src


# Testes: docker compose run --rm testes
FROM base AS testes
RUN pip install --group dev
COPY pytest.ini .
COPY tests ./tests
CMD ["python", "-m", "pytest", "--cov", "--cov-report=term-missing", "--cov-report=html"]


# Servidor: aplica as migrations pendentes e sobe a API na porta 8000.
FROM base AS api
RUN useradd --create-home crm
USER crm
EXPOSE 8000
CMD ["sh", "-c", "python -m alembic upgrade head && exec python -m uvicorn main:app --host 0.0.0.0 --port 8000"]
