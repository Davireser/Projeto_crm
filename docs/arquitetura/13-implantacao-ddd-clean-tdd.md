# Implementação: DDD, Clean Architecture e TDD

Insumo para implementação direta do software. Entidades, RFs e casos de uso deste documento viram código na ordem **domínio → aplicação → infraestrutura/interface**. Nunca começar pelo banco nem pelo controller.

---

## 1. DDD (Domain-Driven Design)

### Entidades de domínio
Extraídas de [04-diagrama-classes.md](04-diagrama-classes.md):

| Entidade | Identidade | Ciclo de vida |
|---|---|---|
| `Cliente` | uuid | cadastrar → atualizar dados de contato |
| `Orcamento` | uuid | novo contato → em negociação → enviado → fechado/perdido (ver [10-diagrama-estados.md](10-diagrama-estados.md)) |
| `Interacao` | uuid | criada e imutável — registro de fato ocorrido |
| `Usuario` | uuid | criar → ativar/desativar |

### Value Objects

| Value Object | Valores | Usado em | Validação |
|---|---|---|---|
| `Telefone` | numero: string | `Cliente.telefone` | formato brasileiro, DDD obrigatório |
| `Email` | endereco: string | `Cliente.email`, `Usuario.email` | formato RFC básico |
| `ValorOrcado` | valor: Decimal (BRL) | `Orcamento.valor` | maior que zero, duas casas decimais |
| `EstagioAtendimento` | enum de 5 valores | `Orcamento.estagio` | conjunto fechado |
| `TipoInteracao` | MENSAGEM, LIGACAO, REUNIAO | `Interacao.tipo` | conjunto fechado |

Value Objects são imutáveis e comparados por valor. A validação acontece na construção — um `Telefone` inválido não chega a existir (RF09).

### Agregados

| Aggregate Root | Entidades internas | Value Objects | Repository |
|---|---|---|---|
| `Cliente` | — | `Telefone`, `Email` | `ClienteRepository` |
| `Orcamento` | `Interacao` (composição) | `EstagioAtendimento`, `ValorOrcado` | `OrcamentoRepository` |
| `Usuario` | — | `Email` | `UsuarioRepository` |

> Regra: `Interacao` só é acessada de fora do agregado através de `Orcamento`. Nunca referenciar `Interacao` diretamente — sempre via `Orcamento.interacoes`. Não existe `InteracaoRepository`.

> Regra: `Cliente` e `Orcamento` são agregados **separados**, ligados por `cliente_id`. Um Orçamento nunca carrega o objeto Cliente inteiro.

### Repository (interfaces)

Interface no domínio, implementação na infraestrutura:

| Interface (domain) | Implementação (adapters) |
|---|---|
| `ClienteRepository` | `ClienteRepositoryPostgres` |
| `OrcamentoRepository` | `OrcamentoRepositoryPostgres` |
| `UsuarioRepository` | `UsuarioRepositoryPostgres` |

Um repository por aggregate root, nunca por entidade filha.

### Domain Service
`UC01 Registrar Novo Contato` cria dois agregados na mesma operação (Cliente e Orçamento). Como não há regra de negócio envolvida — apenas coordenação e transação — isso fica no Use Case, não em Domain Service. Não há Domain Service neste sistema.

### Linguagem ubíqua
`Cliente`, `Orcamento`, `Interacao`, `EstagioAtendimento`, `ValorOrcado`, `Telefone`, `Email`. Nunca `Lead`, `Negociação`, `Deal`, nem nomes genéricos tipo `Manager`, `Helper`, `Processor`, `Service`.

---

## 2. Clean Architecture (camadas)

Mapeamento direto do BCE de [11-boundary-control-entity.md](11-boundary-control-entity.md):

```
backend/src/
│
├── domain/                          # Camada mais interna — zero dependências externas
│   ├── entities/
│   │   ├── cliente.py               # Cliente
│   │   ├── orcamento.py             # Orcamento (+ moverEstagio, definirValor)
│   │   ├── interacao.py             # Interacao
│   │   └── usuario.py               # Usuario, Administrador
│   ├── value_objects/
│   │   ├── telefone.py
│   │   ├── email.py
│   │   ├── valor_orcado.py
│   │   ├── estagio_atendimento.py   # Enum + mapa de transições permitidas
│   │   └── tipo_interacao.py
│   ├── exceptions.py                # TransicaoInvalida, FormatoInvalido, ValorInvalido
│   └── repositories/                # Interfaces (ports)
│       ├── cliente_repository.py
│       ├── orcamento_repository.py
│       └── usuario_repository.py
│
├── application/                     # Use cases — depende só de interfaces do domain
│   └── use_cases/
│       ├── registrar_novo_contato.py
│       ├── mover_estagio.py
│       ├── definir_valor.py
│       ├── registrar_interacao.py
│       ├── consultar_orcamentos.py
│       ├── consultar_metricas.py
│       ├── consultar_historico_cliente.py
│       └── gerenciar_usuarios.py
│
├── adapters/                        # Interface Adapters
│   ├── controllers/                 # Routers FastAPI
│   │   ├── cliente_controller.py
│   │   ├── orcamento_controller.py
│   │   ├── interacao_controller.py
│   │   └── usuario_controller.py
│   ├── repositories/                # Implementações concretas
│   │   ├── cliente_repository_postgres.py
│   │   ├── orcamento_repository_postgres.py
│   │   └── usuario_repository_postgres.py
│   └── schemas/                     # Pydantic — entrada e saída
│       ├── cliente_schema.py
│       ├── orcamento_schema.py
│       └── interacao_schema.py
│
├── infra/                           # Frameworks & Drivers
│   ├── db/
│   │   ├── session.py               # Engine e sessão SQLAlchemy
│   │   └── models.py                # Models ORM (separados das entidades!)
│   ├── config.py                    # Variáveis de ambiente
│   └── security.py                  # JWT e hash de senha
│
└── main.py                          # Composition root — injeta as implementações
```

**Regra de checagem (RNF03):** nenhum import de `sqlalchemy`, `fastapi` ou `pydantic` dentro de `domain/` ou `application/`. Isso é verificado por teste automatizado, não por disciplina.

**Regra de mapeamento:** os models do SQLAlchemy em `infra/db/models.py` são **distintos** das entidades em `domain/entities/`. A tradução acontece nos repositórios concretos. Reaproveitar o model ORM como entidade é o atalho que quebra a arquitetura inteira.

### Frontend correspondente

```
frontend/src/
├── app/
│   ├── (auth)/login/
│   ├── (crm)/kanban/                # UC07, UC03, UC08
│   ├── (crm)/clientes/[id]/         # UC09
│   └── layout.tsx
├── components/
│   ├── kanban/KanbanBoard.tsx       # boundary de UC03/UC07
│   ├── kanban/OrcamentoCard.tsx
│   ├── metricas/MetricasHeader.tsx  # boundary de UC08
│   ├── cliente/ClienteForm.tsx      # boundary de UC01
│   └── interacao/InteracaoForm.tsx  # boundary de UC06
├── hooks/
│   ├── useOrcamentos.ts
│   └── useMoverEstagio.ts           # atualização otimista + rollback
├── services/api.ts                  # cliente HTTP tipado
└── types/                           # espelha os schemas de saída da API (RNF05)
```

---

## 3. TDD (ciclo red → green → refactor)

A implementação segue a ordem abaixo. Cada item começa por um teste que falha.

1. **Unidade de domínio — transição de estágio.** `Orcamento.moverEstagio()` rejeita a transição para FECHADO sem `ValorOrcado` definido (RF03) e rejeita salto de etapa (RF02). Sem banco, sem framework. Este é o primeiro teste do projeto.
2. **Unidade de domínio — Value Objects.** `Telefone` e `Email` recusam formatos inválidos na construção; `ValorOrcado` recusa valor zero ou negativo (RF09).
3. **Unidade de aplicação — métricas.** `ConsultarMetricasUseCase` calcula orçamentos em aberto e taxa de fechamento sobre uma lista em memória (RF06).
4. **Use case com repositório fake in-memory.** `RegistrarNovoContatoUseCase` cria Cliente + Orçamento em NOVO_CONTATO e não persiste nada quando a validação falha (RF01).
5. **Use case com repositório fake.** `MoverEstagioUseCase` propaga `TransicaoInvalida` sem salvar (RF02/RF03).
6. **Integração — repositório.** `OrcamentoRepositoryPostgres` contra banco de teste: round-trip do agregado com suas interações.
7. **Integração — rota.** `PATCH /orcamentos/{id}/estagio` retorna 200 na transição válida e 422 na inválida.
8. **Integração — frontend.** Drag-and-drop no Kanban com Testing Library e mock de API, incluindo o rollback visual em caso de rejeição (RNF02).
9. **Arquitetura.** Teste que falha se `domain/` ou `application/` importarem framework (RNF03).

### Pirâmide esperada
Muitos testes unitários de `Orcamento`, dos Value Objects e dos Use Cases; poucos de integração (repositório e rota); pouquíssimos e2e (fluxo completo do funil no Kanban).

### Rastreabilidade RF → teste

| RF | Caso de Uso | Teste |
|----|-------------|-------|
| RF01 | Registrar Novo Contato | Unidade (Cliente) + Use Case com fake |
| RF02 | Mover Estágio do Orçamento | Unidade (`Orcamento.moverEstagio`) |
| RF03 | Impedir fechamento sem valor | Unidade (guarda `[valorDefinido]`) |
| RF04 | Registrar Interação | Unidade (agregado) + Use Case |
| RF05 | Consultar Painel Kanban | Integração (rota) + frontend |
| RF06 | Consultar Métricas do Funil | Unidade (cálculo puro) |
| RF07 | Consultar Histórico do Cliente | Use Case + Integração (ordenação) |
| RF08 | Múltiplos Orçamentos por Cliente | Integração (repositório) |
| RF09 | Validar Dados de Contato | Unidade (`Telefone`, `Email`) |
| RF10 | Gerenciar Usuários | Use Case + Integração (rota autenticada) |

### Rastreabilidade RNF → verificação

| RNF | Como é verificado |
|-----|-------------------|
| RNF01 | Teste de carga com 500 orçamentos medindo tempo de resposta do endpoint do painel |
| RNF02 | Teste de frontend do drag-and-drop sem reload |
| RNF03 | Teste de arquitetura (item 9) |
| RNF04 | Testes de unidade 1 e 5 — a rejeição acontece antes de qualquer `salvar()` |
| RNF05 | `mypy --strict` no backend, `tsc --noEmit` com `noImplicitAny` no frontend |
| RNF06 | Todos os testes de use case rodam com repositório fake, sem banco |
