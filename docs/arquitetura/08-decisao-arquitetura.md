# Decisões de Arquitetura

## Decisões principais

### 1. Regra de transição no domínio, não na interface
A validação da sequência de estágios e a guarda "não fechar sem valor" vivem em `Orcamento.moverEstagio()`. O drag-and-drop do Kanban é conveniência de UX, não fonte de verdade. Isso atende RNF04 diretamente: mesmo uma chamada direta à API, fora do painel, é rejeitada.

### 2. Orçamento como aggregate root do funil
`Interacao` é acessada apenas através de `Orcamento`. Não existe `InteracaoRepository`. Isso mantém a composição íntegra e evita que uma interação órfã seja persistida sem orçamento.

### 3. Cliente e Orçamento como agregados separados
Um Cliente pode ter muitos Orçamentos ao longo de anos (RF08). Mantê-los no mesmo agregado obrigaria a carregar todo o histórico para mover um único card. A ligação é por `cliente_id`, não por referência de objeto.

### 4. EstagioAtendimento como enum, não como tabela
O conjunto de estágios é fechado, pequeno e conhecido em tempo de compilação. Uma tabela `estagio` traria join em toda consulta do Kanban (RNF01) e abriria espaço para estágios inválidos criados em runtime.

### 5. Clean Architecture em quatro camadas
`domain` / `application` / `adapters` / `infra`, com a regra de dependência apontando para dentro. Atende RNF03 e RNF06 e é o que permite o plano de testes de [13-implantacao-ddd-clean-tdd.md](13-implantacao-ddd-clean-tdd.md) rodar quase todo sem banco.

### 6. Tipagem estrita de ponta a ponta
Pydantic no backend, TypeScript no frontend, sem `any` (RNF05). Os tipos do frontend espelham os schemas de saída da API, de modo que uma mudança de contrato quebra a compilação em vez de quebrar em produção.

## Trade-offs

- **Regra no domínio em vez de CHECK constraint** dá testabilidade e mensagens de erro claras, mas significa que uma escrita direta no banco pode burlar a regra. Aceito: o banco não é acessado fora da aplicação.
- **Enum de estágio em código** é rápido e seguro, mas adicionar um estágio novo exige deploy e migration, não configuração. Aceito: o funil é intencionalmente fixo.
- **Quatro camadas** aumentam o número de arquivos e o custo de escrever uma feature simples, mas são requisito explícito da disciplina e da RNF03. Aceito.
- **Cliente e Orçamento separados** exigem duas escritas em `UC01` (criar Cliente, criar Orçamento) sem transação de agregado único. Mitigado com transação de banco no Use Case.
- **Sem integração com WhatsApp** mantém o escopo viável no semestre, mas exige que o usuário registre a interação manualmente após conversar.

## Riscos e mitigações

### Risco: regra de transição duplicada no frontend e no backend
O Kanban precisa saber quais colunas aceitam o card para dar feedback visual, e o domínio precisa validar de verdade.
**Mitigação:** o frontend consulta as transições permitidas a partir de um mapa exposto pela API, derivado do mesmo enum — nunca reimplementa a regra.

### Risco: desempenho do Kanban com muitos orçamentos
RNF01 exige carga em menos de 2s com 500 orçamentos ativos.
**Mitigação:** índice em `estagio`, projeção enxuta no endpoint do painel (sem carregar interações) e endpoint separado para o detalhe do card.

### Risco: vazamento de framework para o domínio
É o erro mais comum em projeto com Clean Architecture — alguém importa `BaseModel` do Pydantic numa entidade "só para facilitar".
**Mitigação:** teste automatizado de arquitetura que falha a build ao detectar import proibido em `domain/` ou `application/`.

### Risco: estado inconsistente entre UI otimista e backend
O drag-and-drop atualiza a tela antes da resposta da API (RNF02).
**Mitigação:** atualização otimista com rollback explícito — o card volta à coluna de origem ao receber `TransicaoInvalida`.

### Risco: scope creep
CRM é um domínio que atrai funcionalidade sem fim: automação, e-mail, propostas em PDF, integração fiscal.
**Mitigação:** o escopo negativo está registrado no [README](../../README.md) e em [01-visao-produto.md](01-visao-produto.md); qualquer inclusão passa pelo backlog.
