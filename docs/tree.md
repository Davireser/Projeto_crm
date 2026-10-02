# Estrutura de Diretórios e Documentação do Projeto

A estrutura abaixo organiza o projeto em três camadas principais: documentação, backend e frontend. O objetivo é manter o escopo de produto, requisitos, arquitetura e implementação em alinhamento constante.

```text
Projeto_CRM/
├── README.md                                     # Visão geral do projeto e mapa documental
├── docs/                                         # Documentação de produto, arquitetura e backlog
│   ├── documento-software.md                     # Documento consolidado de análise e projeto (entrega da disciplina)
│   ├── especificacoes_tecnicas.md                # Regras de negócio, stack, modelagem e contratos de API
│   ├── apresentacao.md                           # Slide/apresentação do CRM (fonte markdown, modelo em exemplo/slide)
│   ├── apresentacao.pdf                          # Apresentação em PDF, gerada a partir de apresentacao.md
│   ├── tree.md                                   # Estrutura organizada do repositório
│   ├── arquitetura/                              # Documentos de arquitetura (seções do documento consolidado)
│   │   ├── 01-visao-produto.md                   # Visão geral, público-alvo e objetivos do produto
│   │   ├── 02-requisitos-crm.md                  # Tabelas de RF e RNF + critérios de aceitação
│   │   ├── 03-casos-de-uso.md                    # Atores, include, extend e descrições textuais
│   │   ├── 04-diagrama-classes.md                # Classes do domínio, relações e persistência
│   │   ├── 05-diagrama-er.md                     # Modelo de dados e entidades (DER)
│   │   ├── 06-diagrama-sequencia.md              # Fluxos de interação entre boundary/control/entity
│   │   ├── 07-diagrama-componentes.md            # Componentes e dependências entre camadas
│   │   ├── 08-decisao-arquitetura.md             # Decisões de arquitetura, trade-offs e riscos
│   │   ├── 09-diagrama-objetos.md                # Instâncias validando cardinalidades
│   │   ├── 10-diagrama-estados.md                # Ciclo de vida do Orçamento
│   │   ├── 11-boundary-control-entity.md         # Mapeamento BCE por caso de uso
│   │   ├── 12-diagrama-atividades.md             # Fluxo ponta a ponta contato → fechamento/perda
│   │   └── 13-implantacao-ddd-clean-tdd.md       # DDD, Clean Architecture e plano de testes
│   ├── requisitos/                               # Requisitos funcionais e não funcionais detalhados
│   │   ├── requisitos-funcionais.md              # RFs do sistema
│   │   └── requisitos-nao-funcionais.md          # RNFs da solução
│   ├── backlog/                                  # Planejamento do produto e execução
│   │   └── backlog-crm.md                        # Priorização por MVP e evolução
│   └── imagens-diagramas/                        # Exportações PNG/SVG dos diagramas Mermaid
├── backend/                                      # Aplicação de API e regras de negócio
│   ├── src/
│   │   ├── domain/                               # Camada mais interna — zero dependência de framework
│   │   │   ├── entities/                         # Cliente, Orcamento, Interacao, Usuario
│   │   │   ├── value_objects/                    # Telefone, Email, ValorOrcado, EstagioAtendimento
│   │   │   └── repositories/                     # Interfaces (ports) dos repositórios
│   │   ├── application/                          # Casos de uso
│   │   │   └── use_cases/                        # RegistrarNovoContato, MoverEstagio, etc.
│   │   ├── adapters/                             # Adaptadores de entrada e saída
│   │   │   ├── controllers/                      # Routers FastAPI
│   │   │   ├── repositories/                     # Implementações PostgreSQL
│   │   │   └── schemas/                          # Schemas Pydantic de entrada/saída
│   │   ├── infra/                                # Frameworks e drivers
│   │   │   ├── db/                               # SQLAlchemy, sessão, models
│   │   │   ├── config.py                         # Variáveis de ambiente
│   │   │   └── security.py                       # JWT e hash de senha
│   │   └── main.py                               # Ponto de entrada da API
│   ├── tests/
│   │   ├── unit/                                 # Domínio e use cases (repositório fake)
│   │   ├── integration/                          # Repositórios Postgres e rotas
│   │   └── e2e/                                  # Fluxo completo do funil
│   ├── alembic/                                  # Migrations
│   ├── pyproject.toml
│   └── pytest.ini
├── frontend/                                     # Aplicação web do painel Kanban
│   ├── src/
│   │   ├── app/
│   │   │   ├── (auth)/                           # Login e sessão
│   │   │   ├── (crm)/                            # Kanban, cliente, métricas
│   │   │   └── layout.tsx
│   │   ├── components/                           # KanbanBoard, OrcamentoCard, formulários
│   │   ├── hooks/                                # Estado do funil e chamadas de API
│   │   ├── services/                             # Cliente HTTP da API
│   │   ├── types/                                # Tipos espelhando os schemas do backend
│   │   ├── utils/
│   │   └── lib/
│   ├── tests/
│   ├── .eslintrc.json
│   ├── .prettierrc
│   ├── next.config.js
│   ├── package.json
│   ├── tailwind.config.ts
│   ├── tsconfig.json
│   └── README.md
├── .gitignore
├── .env.example
└── .vscode/
```

## Observações de organização
- A pasta `docs` concentra o produto, o escopo e a arquitetura de decisão; `documento-software.md` é a versão consolidada e `arquitetura/` é a mesma matéria dividida por seção.
- O backend concentra as regras de transição de estágio, a validação de valor do orçamento e a persistência.
- O frontend cuida do painel Kanban, dos formulários de contato/interação e da exibição das métricas.
- A separação entre `domain`, `application`, `adapters` e `infra` é um princípio da arquitetura: nenhum import de SQLAlchemy ou Pydantic pode aparecer em `domain/` ou `application/`.
- A pasta `exemplo/` é material de referência local e está no `.gitignore` — não vai para o repositório remoto.

## Documento de referência
Para uma leitura completa do projeto, recomenda-se seguir esta ordem:
1. [README.md](../README.md)
2. [docs/arquitetura/01-visao-produto.md](arquitetura/01-visao-produto.md)
3. [docs/requisitos](requisitos)
4. [docs/arquitetura](arquitetura)
5. [docs/especificacoes_tecnicas.md](especificacoes_tecnicas.md)
6. [docs/backlog](backlog)
