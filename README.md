# CRM de Atendimento e Orçamentos

**Disciplina:** Laboratório de Programação Web (G08LPWE0.01) — CEFET-MG
**Domínio:** CRM para pequenos negócios que vendem por contato direto (WhatsApp, ligação, indicação), como uma empresa de embalagens.

## Resumo Executivo
Este projeto consiste na criação de um CRM enxuto para pequenos negócios que não vendem por e-commerce, e sim por atendimento direto. A solução organiza o funil de atendimento em um painel Kanban, registra o histórico de interações com cada cliente e garante, no domínio, que nenhum orçamento avance de estágio de forma inconsistente.

O produto é organizado em torno de um funil de cinco estágios — Novo Contato, Em Negociação, Orçamento Enviado, Fechado e Perdido — com regras de transição validadas na camada de domínio, não apenas na interface.

## Objetivo do Projeto
O objetivo principal é substituir o controle informal de atendimentos (caderno, planilha, conversas soltas no WhatsApp) por um funil visual e rastreável, sem exigir a complexidade de um CRM comercial. A solução atua como um organizador de atendimento e conversão, conectando cliente, orçamento e histórico de interações em um único fluxo.

## Escopo Principal
### 1. Cadastro e qualificação de contato
- registro de Cliente com telefone e e-mail validados;
- criação automática de um Orçamento no estágio "Novo Contato";
- vínculo de múltiplos Orçamentos ao mesmo Cliente ao longo do tempo.

### 2. Funil de atendimento (Kanban)
- painel com os Orçamentos agrupados por estágio;
- movimentação por drag-and-drop, sem recarregar a página;
- validação da sequência de transições no domínio.

### 3. Histórico de interações
- registro de mensagens, ligações e reuniões vinculadas a um Orçamento;
- linha do tempo cronológica por Cliente.

### 4. Métricas do funil
- quantidade de orçamentos em aberto;
- taxa de fechamento.

## Nomenclatura adotada
- O produto é chamado de **CRM de Atendimento e Orçamentos**.
- A unidade central de trabalho é o **Orçamento** (aggregate root do funil).
- O funil de atendimento é o **EstagioAtendimento**, um enum de cinco valores.
- Cada registro de contato é uma **Interação**.

Essa padronização é a linguagem ubíqua do projeto e vale para código, banco e documentação — nunca `Lead`, `Negociação` ou nomes genéricos tipo `Manager`.

## Arquitetura Geral
O sistema foi estruturado em duas frentes principais, ambas sob Clean Architecture:

### Frontend
- Next.js 16 (App Router, Turbopack, Cache Components) + React 19 + TypeScript estrito, sem `any`
- TailwindCSS + shadcn/ui; painel Kanban com arraste por mouse e teclado (dnd-kit)
- camadas `domain` (TypeScript puro, testado com TDD) / `application` / `infra`, com o sentido das dependências conferido por teste
- TanStack Query offline first: cache persistido no navegador e alterações pausadas sem rede
- Vitest + React Testing Library (testes unitários e de interface)

### Backend
- FastAPI + Python
- PostgreSQL + SQLAlchemy + Alembic
- camadas `domain` / `application` / `adapters` / `infra`
- regras de transição de estágio isoladas de framework

## Como rodar
Pré-requisito: Docker (no Windows, o Docker Desktop). Na raiz do projeto:

```bash
cp .env.example .env               # no PowerShell: copy .env.example .env
docker compose up --build          # PostgreSQL + API + frontend
```

- Aplicação: http://localhost:3000 (entra direto no painel depois do login)
- Swagger (documentação interativa da API): http://localhost:8000/docs
- Banco pelo navegador (pgAdmin): http://localhost:5050 — login `admin@crm.com` / `admin123` (configurável no `.env`); servidor "CRM (Docker)" já cadastrado, senha do PostgreSQL `crm`
- Primeiro administrador: `docker compose exec api python src/criar_administrador.py --nome "Seu Nome" --email voce@email.com`
- Esqueceu a senha: `docker compose exec api python src/redefinir_senha.py --email voce@email.com` (a nova senha é pedida no terminal)
- Testes do backend com cobertura: `docker compose run --rm testes` (relatório em `backend/htmlcov/index.html`; meta mínima de 80%)

Abra a aplicação por `http://localhost:3000`: em produção o cookie de sessão é `Secure`, e os navegadores só o aceitam sem HTTPS no endereço `localhost`.

### Frontend em modo de desenvolvimento
Com o banco e a API no Docker (`docker compose up -d db api`), dentro de `frontend/` (Node.js 20.9 ou mais novo):

```bash
npm install
npm run dev          # http://localhost:3000, recarrega a cada alteração
npm test             # Vitest em modo observação; npm run test:cov gera a cobertura (meta de 80%)
npm run lint         # ESLint; npm run typecheck confere os tipos
```

O Next fala com a API pelo endereço de `API_URL` (padrão `http://localhost:8000`); o navegador só fala com o próprio Next, em `/api`.

Detalhes em [docs/plano-backend.md](docs/plano-backend.md) e [docs/plano-frontend.md](docs/plano-frontend.md).

## Estrutura da documentação
```text
Projeto_CRM/
├── README.md
├── docs/
│   ├── documento-software.md
│   ├── especificacoes_tecnicas.md
│   ├── tree.md
│   ├── arquitetura/
│   │   ├── 01-visao-produto.md
│   │   ├── 02-requisitos-crm.md
│   │   ├── 03-casos-de-uso.md
│   │   ├── 04-diagrama-classes.md
│   │   ├── 05-diagrama-er.md
│   │   ├── 06-diagrama-sequencia.md
│   │   ├── 07-diagrama-componentes.md
│   │   ├── 08-decisao-arquitetura.md
│   │   ├── 09-diagrama-objetos.md
│   │   ├── 10-diagrama-estados.md
│   │   ├── 11-boundary-control-entity.md
│   │   ├── 12-diagrama-atividades.md
│   │   └── 13-implantacao-ddd-clean-tdd.md
│   ├── requisitos/
│   │   ├── requisitos-funcionais.md
│   │   └── requisitos-nao-funcionais.md
│   ├── backlog/
│   │   └── backlog-crm.md
│   └── imagens-diagramas/
├── backend/
│   ├── src/
│   ├── tests/
│   ├── alembic/
│   ├── Dockerfile
│   ├── pyproject.toml
│   └── pytest.ini
├── frontend/
│   ├── src/                 # app/ (rotas), domain/, application/, infra/, components/, hooks/, lib/
│   ├── tests/               # unit/, ui/ e arquitetura/
│   ├── Dockerfile
│   ├── package.json
│   ├── next.config.ts
│   └── tsconfig.json
├── docker/                  # init.sql do PostgreSQL e servidores do pgAdmin
├── docker-compose.yml
├── .gitignore
└── .env.example
```

## Fora de escopo
O projeto não inclui:
- integração oficial com a API do WhatsApp Business;
- emissão de nota fiscal, boleto ou cobrança;
- gestão de estoque, catálogo de produtos ou logística;
- automação de marketing, disparo em massa e e-mail marketing;
- portal de autoatendimento para o cliente final;
- aplicativo nativo mobile.

## Resultado esperado
A solução deve entregar um funil de atendimento visível, rastreável e consistente, transformando o controle informal de orçamentos em um processo mensurável — com regras de negócio testáveis fora do framework, conforme exigido pela disciplina.

## Referências documentais
- [docs/documento-software.md](docs/documento-software.md) — documento consolidado de análise e projeto
- [docs/apresentacao.pdf](docs/apresentacao.pdf) — apresentação/slide do CRM em PDF ([fonte em docs/apresentacao.md](docs/apresentacao.md))
- [docs/especificacoes_tecnicas.md](docs/especificacoes_tecnicas.md)
- [docs/tree.md](docs/tree.md)
- [docs/arquitetura](docs/arquitetura)
- [docs/requisitos](docs/requisitos)
- [docs/backlog](docs/backlog)
