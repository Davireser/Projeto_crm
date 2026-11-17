# Deploy — Neon (PostgreSQL) + Docker Hub + Render (API) + Vercel (frontend)

```text
Pull request ──► testes do backend (pytest, mypy, ruff) + frontend (vitest, lint, build)

Push na main ──► testes passam
                   ├──► imagem da API no Docker Hub ──► Deploy Hook do Render
                   └──► deploy do frontend na Vercel
```

| Arquivo | Função |
| --- | --- |
| `backend/Dockerfile` (alvo `api`) | Imagem da API. Aplica as migrations ao subir e usa a porta de `$PORT` (o Render define) |
| `frontend/vercel.json` | Desliga o deploy automático da Vercel a cada push: quem publica é o pipeline, depois dos testes |
| `.github/workflows/ci-cd.yml` | Testes, imagem no Docker Hub e os dois deploys |

Como as peças conversam: o navegador só fala com o Next na Vercel (`/api/...`); o servidor do
Next repassa para a API no Render usando `API_URL`. O cookie de sessão fica no domínio da Vercel,
então não há problema de cookie entre domínios.

A ordem abaixo importa: cada passo usa um valor do anterior.

---

## 1. Banco no Neon

1. Em [neon.tech](https://neon.tech), crie um projeto: nome `crm-orcamentos`, Postgres 17,
   região **AWS US East (Ohio)** — a mesma que você vai escolher no Render.
2. No painel do projeto, clique em **Connect**, **desligue "Connection pooling"** e copie a
   connection string. Ela vem assim:

   ```text
   postgresql://neondb_owner:SENHA@ep-xxxx.us-east-2.aws.neon.tech/neondb?sslmode=require&channel_binding=require
   ```

3. Apague o `&channel_binding=require` do final. Fica:

   ```text
   postgresql://neondb_owner:SENHA@ep-xxxx.us-east-2.aws.neon.tech/neondb?sslmode=require
   ```

> Não troque o prefixo para `postgresql+asyncpg://`: este backend usa o driver **pg8000**. A API já
> converte `postgresql://...?sslmode=require` sozinha (`infra/db/session.py`).
> A conexão direta (sem pooling) evita problemas do pooler com o pg8000; para um Web Service
> só, ela é suficiente.

Essa URL é o `DATABASE_URL` do passo 3. Não a coloque em nenhum arquivo do repositório.

## 2. Docker Hub

1. Em [hub.docker.com](https://hub.docker.com), anote seu **username**.
2. Crie o repositório **`crm-backend`** (público é mais simples: o Render baixa sem credenciais).
3. **Account settings → Personal access tokens → Generate new token**, com permissão
   **Read & Write**. Copie o token: é o secret `DOCKERHUB_TOKEN`.

A imagem só aparece lá depois do primeiro push na main (passo 6). Para criar o serviço no Render
antes disso, publique a primeira vez à mão (PowerShell, na raiz do projeto):

```powershell
docker login -u SEU_USUARIO
docker build --target api -t SEU_USUARIO/crm-backend:latest backend
docker push SEU_USUARIO/crm-backend:latest
```

## 3. API no Render

1. Em [dashboard.render.com](https://dashboard.render.com): **New → Web Service → Existing Image**.
2. **Image URL**: `docker.io/SEU_USUARIO/crm-backend:latest`
3. **Region**: Ohio (a mesma do Neon). **Instance type**: Free.
4. **Environment Variables**:

   | Variável | Valor |
   | --- | --- |
   | `DATABASE_URL` | a URL do Neon do passo 1 |
   | `JWT_SECRET` | um valor aleatório longo (veja abaixo) |
   | `ENVIRONMENT` | `production` |
   | `CORS_ORIGINS` | `https://SEU-PROJETO.vercel.app` (preencha depois do passo 4) |
   | `FUSO_HORARIO` | `America/Sao_Paulo` |

   Gerar o `JWT_SECRET` (PowerShell): `-join ((48..57)+(97..122) | Get-Random -Count 48 | % {[char]$_})`.
   Com `ENVIRONMENT=production`, a API se recusa a subir com o segredo padrão.

5. Em **Advanced → Health Check Path**: `/health`.
6. Crie o serviço. Nos **Logs** deve aparecer a migration do Alembic e
   `Uvicorn running on http://0.0.0.0:10000`. Teste:

   ```powershell
   curl.exe https://SEU-SERVICO.onrender.com/health
   # {"status":"ok"}
   ```

7. **Settings → Deploy Hook**: copie a URL. É o secret `RENDER_DEPLOY_HOOK_URL`.

### Primeiro administrador

O banco do Neon começa sem usuários. Depois que a API subiu uma vez (as tabelas já existem), crie
o administrador do seu computador, apontando para o Neon (PowerShell, dentro de `backend/`):

```powershell
$env:DATABASE_URL = "URL_DO_NEON"
.\.venv\Scripts\python.exe src\criar_administrador.py --nome "Seu Nome" --email voce@email.com
Remove-Item Env:DATABASE_URL
```

A senha é pedida no terminal. O script só funciona com o cadastro de usuários vazio.

## 4. Frontend na Vercel

1. Em [vercel.com](https://vercel.com): **Add New → Project**, importe o repositório do GitHub.
2. **Root Directory**: `frontend`. O framework (Next.js) é detectado sozinho.
3. **Environment Variables**: `API_URL` = `https://SEU-SERVICO.onrender.com` (sem `/api/v1`
   e sem barra no final).
4. **Deploy**. Anote a URL (`https://SEU-PROJETO.vercel.app`) e volte ao Render para preencher
   `CORS_ORIGINS` com ela.
5. Token e IDs para o pipeline:
   - **Account Settings → Tokens → Create**: é o `VERCEL_TOKEN`.
   - IDs (PowerShell, dentro de `frontend/`):

     ```powershell
     npx vercel link
     Get-Content .vercel\project.json
     ```

     `orgId` é o `VERCEL_ORG_ID`; `projectId` é o `VERCEL_PROJECT_ID`. A pasta `.vercel` já está
     no `.gitignore`.

## 5. Secrets no GitHub

No repositório: **Settings → Secrets and variables → Actions → New repository secret**.

| Secret | De onde vem |
| --- | --- |
| `DOCKERHUB_USERNAME` | passo 2 |
| `DOCKERHUB_TOKEN` | passo 2 |
| `RENDER_DEPLOY_HOOK_URL` | passo 3.7 |
| `VERCEL_TOKEN` | passo 4.5 |
| `VERCEL_ORG_ID` | passo 4.5 |
| `VERCEL_PROJECT_ID` | passo 4.5 |

## 6. Pipeline

A cada push na main, `.github/workflows/ci-cd.yml` roda:

1. **backend-tests** — Python 3.14 com um PostgreSQL de teste: `ruff`, `mypy` e `pytest`.
2. **frontend-tests** — Node 24: `lint`, `typecheck`, `vitest` e `next build`.
3. **docker-build-push** — publica `crm-backend:latest` e `crm-backend:<sha do commit>`.
4. **deploy-backend-render** — chama o Deploy Hook; o Render baixa a `:latest` e reinicia.
5. **deploy-frontend** — `vercel pull`, `vercel build --prod` e `vercel deploy --prebuilt --prod`.

Pull requests só rodam 1 e 2. Para rodar tudo sem commit novo: aba **Actions → CI/CD → Run workflow**.

## 7. Conferindo

1. **Actions**: os 5 jobs verdes.
2. **Docker Hub**: tags `latest` e a do commit.
3. `curl.exe https://SEU-SERVICO.onrender.com/health` responde `{"status":"ok"}`.
4. Abra a URL da Vercel, entre com o administrador e faça o fluxo: novo contato, mover no Kanban,
   valor, interação, métricas.

## 8. Problemas comuns

| Sintoma | O que fazer |
| --- | --- |
| API não sobe: `Defina JWT_SECRET` | Falta `JWT_SECRET` no Render (com `ENVIRONMENT=production` o padrão é recusado). |
| Erro de conexão com o banco | A URL tem `?sslmode=require`? Tirou o `channel_binding`? Usou a conexão **sem** pooling? |
| Neon: `Endpoint ID is not specified` | Coloque o ID do endpoint antes da senha: `postgresql://neondb_owner:endpoint=ep-xxxx;SENHA@ep-xxxx...` |
| Login na Vercel dá erro de rede | `API_URL` na Vercel aponta para o Render, sem `/api/v1` e sem barra final? Depois de mudar, faça um redeploy. |
| Primeira requisição demora ~1 minuto | Normal no plano Free: o Render hiberna após 15 min sem uso. |
| Push na main não publica a Vercel | É de propósito (`vercel.json`): quem publica é o pipeline. Veja o job `deploy-frontend`. |
| `docker push` falha no Actions | Confira `DOCKERHUB_USERNAME`/`DOCKERHUB_TOKEN` e se o token tem permissão de escrita. |
