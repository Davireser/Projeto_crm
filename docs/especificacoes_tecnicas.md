# Especificações Técnicas

Documento de referência para implementação. Consolida stack, contratos de API, modelagem e regras de negócio executáveis. As decisões que sustentam estas escolhas estão em [arquitetura/08-decisao-arquitetura.md](arquitetura/08-decisao-arquitetura.md).

---

## 1. Stack

### Backend
| Item | Escolha | Motivo |
|------|---------|--------|
| Linguagem | Python 3.12+ | Exigência da disciplina; tipagem opcional estrita via mypy |
| Framework web | FastAPI | Validação por Pydantic, OpenAPI automático, assíncrono |
| ORM | SQLAlchemy 2.x | Models separados das entidades de domínio |
| Migrations | Alembic | Versionamento de esquema |
| Banco | PostgreSQL 16 | Requisito da disciplina |
| Testes | pytest | Fixtures e parametrização |
| Tipagem | mypy `--strict` | RNF05 |

### Frontend
| Item | Escolha | Motivo |
|------|---------|--------|
| Framework | Next.js (App Router) | Roteamento por pastas, Server Components |
| Linguagem | TypeScript estrito | RNF05, sem `any` |
| Estilo | Tailwind CSS | Consistência sem CSS disperso |
| Componentes | shadcn/ui | Base acessível sobre Radix |
| Drag-and-drop | dnd-kit | Acessível por teclado, sem dependência legada |
| Testes | Vitest + Testing Library | RNF02 |

---

## 2. Modelo de dados

Esquema em [arquitetura/05-diagrama-er.md](arquitetura/05-diagrama-er.md). Pontos de atenção na implementação:

- `orcamento.valor` é **nullable** — a ausência de valor é um estado válido e significativo (RF03);
- `orcamento.estagio` é `VARCHAR` com CHECK, não tipo ENUM nativo do Postgres — evita migration dolorosa ao evoluir o conjunto;
- `interacao` tem FK `ON DELETE CASCADE` (composição);
- `cliente` tem FK reversa `ON DELETE RESTRICT` — cliente com histórico não é apagado;
- todos os identificadores são UUID v4 gerados na aplicação, não pelo banco.

### Índices

```sql
CREATE INDEX idx_orcamento_estagio ON orcamento (estagio);
CREATE INDEX idx_orcamento_cliente_id ON orcamento (cliente_id);
CREATE INDEX idx_interacao_orcamento_data ON interacao (orcamento_id, data_hora DESC);
```

---

## 3. Regras de negócio executáveis

### RN01 — Transições de estágio permitidas (RF02)

```
NOVO_CONTATO       -> EM_NEGOCIACAO, PERDIDO
EM_NEGOCIACAO      -> ORCAMENTO_ENVIADO, PERDIDO
ORCAMENTO_ENVIADO  -> FECHADO, PERDIDO
FECHADO            -> (terminal)
PERDIDO            -> (terminal)
```

Qualquer par fora desta lista lança `TransicaoInvalida`.

### RN02 — Guarda de valor (RF03)
Transições para `ORCAMENTO_ENVIADO` e `FECHADO` exigem `valor is not None`. A verificação acontece em `Orcamento.moverEstagio()`, antes de qualquer efeito.

### RN03 — Data de fechamento
Ao entrar em `FECHADO` ou `PERDIDO`, `data_fechamento` recebe a data corrente. Nos demais estágios permanece nula.

### RN04 — Validação de telefone (RF09)
Formato brasileiro com DDD, 10 ou 11 dígitos após a remoção de máscara. Armazenado normalizado (somente dígitos); a máscara é responsabilidade da exibição.

### RN05 — Validação de e-mail (RF09)
Formato `local@dominio.tld`, normalizado para minúsculas.

### RN06 — Valor orçado
Decimal positivo com duas casas, maior que zero. Zero e negativo são rejeitados na construção do Value Object.

### RN07 — Métricas do funil (RF06)
- **Orçamentos em aberto** = contagem de orçamentos cujo estágio não é `FECHADO` nem `PERDIDO`.
- **Taxa de fechamento** = `FECHADO / (FECHADO + PERDIDO)`, expressa em percentual. Quando não há orçamentos concluídos, a taxa é indefinida e a interface exibe "—", não zero.

### RN08 — Ordenação do histórico (RF07)
Interações de todos os orçamentos do cliente, ordenadas por `data_hora` ascendente, agrupadas visualmente por orçamento.

---

## 4. Contratos de API

Base: `/api/v1`. Todas as rotas exigem `Authorization: Bearer <token>`, exceto o login.

| Método | Rota | Caso de uso | Sucesso | Erros |
|--------|------|-------------|---------|-------|
| `POST` | `/auth/login` | — | 200 + token | 401 credenciais inválidas |
| `POST` | `/clientes` | UC01 | 201 + cliente e orçamento criados | 422 telefone/e-mail inválido |
| `GET` | `/clientes/{id}` | UC09 | 200 + cliente com orçamentos | 404 |
| `GET` | `/clientes/{id}/historico` | UC09 | 200 + interações cronológicas | 404 |
| `GET` | `/orcamentos` | UC07 | 200 + orçamentos agrupados por estágio | — |
| `PATCH` | `/orcamentos/{id}/estagio` | UC03 | 200 + orçamento atualizado | 404, 422 `TransicaoInvalida` |
| `PATCH` | `/orcamentos/{id}/valor` | UC05 | 200 + orçamento atualizado | 404, 422 valor inválido |
| `POST` | `/orcamentos/{id}/interacoes` | UC06 | 201 + interação criada | 404, 422 |
| `GET` | `/metricas/funil` | UC08 | 200 + métricas | — |
| `GET` | `/usuarios` | UC10 | 200 + lista | 403 perfil insuficiente |
| `POST` | `/usuarios` | UC10 | 201 | 403, 409 e-mail duplicado |
| `PATCH` | `/usuarios/{id}` | UC10 | 200 | 403, 422 auto-desativação |

### Formato de erro

```json
{
  "erro": "TransicaoInvalida",
  "mensagem": "Não é possível mover de NOVO_CONTATO para FECHADO",
  "campo": "estagio"
}
```

### Exemplo — `PATCH /orcamentos/{id}/estagio`

Requisição:
```json
{ "estagio": "ORCAMENTO_ENVIADO" }
```

Resposta 200:
```json
{
  "id": "o7b3...",
  "clienteId": "c1a2...",
  "estagio": "ORCAMENTO_ENVIADO",
  "valor": "4200.00",
  "dataAbertura": "2026-09-01",
  "dataFechamento": null
}
```

Resposta 422 (guarda de valor, RN02):
```json
{
  "erro": "TransicaoInvalida",
  "mensagem": "Orçamento sem valor definido não pode ser enviado",
  "campo": "valor"
}
```

### Endpoint de apoio ao frontend
`GET /orcamentos/transicoes` devolve o mapa de transições permitidas (RN01), derivado do mesmo enum usado pelo domínio. O Kanban usa esse mapa para destacar colunas válidas durante o arraste — **nunca** reimplementa a regra em TypeScript.

---

## 5. Projeções e desempenho

Para atender RNF01, `GET /orcamentos` devolve uma projeção enxuta por card:

```json
{
  "id": "o7b3...",
  "clienteNome": "Embalagens ABC",
  "estagio": "EM_NEGOCIACAO",
  "valor": null,
  "dataAbertura": "2026-09-01",
  "qtdInteracoes": 2
}
```

As interações completas são carregadas apenas ao abrir o detalhe do card.

---

## 6. Configuração de ambiente

Variáveis em `.env`, documentadas em `.env.example`:

| Variável | Descrição |
|----------|-----------|
| `DATABASE_URL` | String de conexão do PostgreSQL |
| `JWT_SECRET` | Segredo de assinatura do token |
| `JWT_EXPIRATION_MINUTES` | Validade do token |
| `CORS_ORIGINS` | Origens permitidas para o frontend |
| `NEXT_PUBLIC_API_URL` | URL base da API consumida pelo frontend |

O arquivo `.env` está no `.gitignore`; apenas `.env.example` é versionado.

---

## 7. Convenções de código

- **Nomes de domínio em português**, seguindo a linguagem ubíqua: `Orcamento`, `moverEstagio`, `ValorOrcado`. Termos técnicos permanecem em inglês (`repository`, `use_case`).
- **Backend:** `snake_case` para arquivos, módulos e funções; `PascalCase` para classes.
- **Frontend:** `PascalCase` para componentes; `camelCase` para hooks e funções; a API entrega JSON em `camelCase`.
- **Sem `Manager`, `Helper`, `Util`, `Service`** em nomes de classe de domínio.
- **Models ORM nunca são entidades de domínio.** A conversão acontece no repositório concreto.
- **Commits** referenciam o RF ou RNF atendido quando aplicável.
