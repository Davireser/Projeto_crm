# Backlog do CRM de Atendimento e Orçamentos

Priorização por fase. A ordem segue a regra de implementação de [../arquitetura/13-implantacao-ddd-clean-tdd.md](../arquitetura/13-implantacao-ddd-clean-tdd.md): domínio primeiro, interface por último.

---

## Fase 0 — Fundação

| # | Item | RF/RNF | Critério de pronto |
|---|------|--------|--------------------|
| 0.1 | Estrutura de pastas do backend em quatro camadas | RNF03 | `domain`, `application`, `adapters`, `infra` criados com `__init__` |
| 0.2 | Teste de arquitetura que proíbe framework em `domain`/`application` | RNF03 | Build falha ao inserir `import fastapi` em `domain/` |
| 0.3 | Projeto Next.js com TypeScript estrito e Tailwind | RNF05 | `tsc --noEmit` limpo com `noImplicitAny` |
| 0.4 | Docker Compose com PostgreSQL | RNF09 | `docker compose up` sobe banco acessível |
| 0.5 | `mypy --strict` e lint em CI | RNF05 | Pipeline verde em commit limpo |

---

## Fase 1 — MVP: o funil funciona

O objetivo da fase é ter o funil operando ponta a ponta com as regras de negócio corretas. Sem isso, nada mais importa.

| # | Item | RF | Critério de pronto |
|---|------|----|--------------------|
| 1.1 | Value Objects `Telefone`, `Email`, `ValorOrcado` | RF09 | Formato inválido lança exceção na construção; testes de unidade passando |
| 1.2 | Enum `EstagioAtendimento` + mapa de transições permitidas | RF02 | Mapa reflete exatamente [10-diagrama-estados.md](../arquitetura/10-diagrama-estados.md) |
| 1.3 | Entidade `Orcamento` com `moverEstagio()` e guarda de valor | RF02, RF03 | Salto de etapa e fechamento sem valor rejeitados em teste de unidade |
| 1.4 | Entidade `Cliente` | RF01 | Cliente só existe com telefone e e-mail válidos |
| 1.5 | Interfaces de repositório + fake in-memory | RNF06 | Use cases testáveis sem banco |
| 1.6 | `RegistrarNovoContatoUseCase` | RF01 | Cria Cliente + Orçamento em NOVO_CONTATO; nada é salvo se a validação falhar |
| 1.7 | `MoverEstagioUseCase` | RF02, RF03 | Propaga `TransicaoInvalida` sem chamar `salvar()` |
| 1.8 | Models SQLAlchemy + migration inicial | RNF08 | Tabelas de [05-diagrama-er.md](../arquitetura/05-diagrama-er.md) criadas via Alembic |
| 1.9 | Repositórios PostgreSQL | RNF08 | Round-trip do agregado em teste de integração |
| 1.10 | Rotas `POST /clientes` e `PATCH /orcamentos/{id}/estagio` | RF01, RF02 | 200 na transição válida, 422 na inválida |
| 1.11 | Painel Kanban com colunas por estágio | RF05 | Orçamentos aparecem na coluna correta |
| 1.12 | Drag-and-drop com atualização otimista e rollback | RNF02 | Card retorna à origem quando o backend rejeita |
| 1.13 | Formulário de novo contato | RF01 | Erro de validação exibido campo a campo |

**Definição de pronto da fase:** é possível registrar um contato e conduzi-lo até Fechado ou Perdido pela interface, com todas as transições inválidas bloqueadas pelo domínio.

---

## Fase 2 — Histórico e contexto

| # | Item | RF | Critério de pronto |
|---|------|----|--------------------|
| 2.1 | Entidade `Interacao` dentro do agregado `Orcamento` | RF04 | Interação só é criada via `Orcamento.registrarInteracao()` |
| 2.2 | `RegistrarInteracaoUseCase` + rota | RF04 | Interação persistida com data/hora do sistema |
| 2.3 | Formulário de interação no card | RF04 | Tipo e conteúdo enviados sem sair do painel |
| 2.4 | `DefinirValorUseCase` + formulário de valor | RF03 | Definir valor libera as transições guardadas |
| 2.5 | `ConsultarHistoricoClienteUseCase` | RF07 | Interações de todos os orçamentos do cliente, em ordem cronológica |
| 2.6 | Tela de linha do tempo do cliente | RF07, RF08 | Orçamentos anteriores visíveis junto ao atual |
| 2.7 | Índices de banco (`estagio`, `cliente_id`, `orcamento_id + data`) | RNF01 | Consultas do painel e do histórico usam índice |

---

## Fase 3 — Medição e administração

| # | Item | RF | Critério de pronto |
|---|------|----|--------------------|
| 3.1 | `ConsultarMetricasUseCase` | RF06 | Cálculo puro, testado sem banco |
| 3.2 | Cabeçalho de métricas no painel | RF06 | Orçamentos em aberto e taxa de fechamento visíveis |
| 3.3 | Entidade `Usuario` e autenticação JWT | RNF07 | Rotas do CRM exigem token válido |
| 3.4 | Perfil `Administrador` e autorização por perfil | RF10, RNF07 | Rota de gestão de usuários nega perfil comum |
| 3.5 | `GerenciarUsuariosUseCase` + tela de usuários | RF10 | Criar, editar e desativar; auto-desativação bloqueada |
| 3.6 | Teste de carga com 500 orçamentos | RNF01 | Painel abaixo de 2s |

---

## Fase 4 — Evolução (fora do MVP)

Itens desejáveis, sem compromisso de entrega no semestre:

- filtro do Kanban por período, valor ou tipo de embalagem;
- busca de cliente por nome, telefone ou empresa;
- lembrete de follow-up para orçamentos parados há N dias;
- exportação do funil em CSV;
- gráfico de evolução mensal da taxa de fechamento;
- registro de motivo da perda, com categorização.

---

## Fora de escopo (não entram no backlog)

Registrados aqui para evitar reabertura de discussão a cada sprint:

- integração oficial com a API do WhatsApp Business;
- emissão de nota fiscal, boleto ou cobrança;
- catálogo de produtos, estoque e logística;
- automação de marketing e disparo em massa;
- portal de autoatendimento para o cliente final;
- aplicativo nativo mobile.

Ver [../arquitetura/08-decisao-arquitetura.md](../arquitetura/08-decisao-arquitetura.md), seção "Risco: scope creep".
