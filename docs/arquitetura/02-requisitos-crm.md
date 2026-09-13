# Requisitos do CRM

## Requisitos funcionais (RF)

| ID | Descrição | Prioridade | Ator/Origem |
|----|-----------|------------|-------------|
| RF01 | Sistema deve permitir que o Usuário registre um novo contato, criando um Cliente e um Orçamento no estágio "Novo Contato" | Alta | Usuário |
| RF02 | Sistema deve permitir que o Usuário mova o estágio de um Orçamento respeitando a sequência Novo Contato → Em Negociação → Orçamento Enviado → Fechado/Perdido | Alta | Usuário |
| RF03 | Sistema deve impedir que um Orçamento seja marcado como "Fechado" sem um valor definido | Alta | Usuário |
| RF04 | Sistema deve permitir que o Usuário registre uma Interação (mensagem, ligação ou reunião) vinculada a um Orçamento | Alta | Usuário |
| RF05 | Sistema deve exibir um painel Kanban com os Orçamentos organizados por estágio | Alta | Usuário |
| RF06 | Sistema deve calcular métricas simples do funil: quantidade de orçamentos em aberto e taxa de fechamento | Média | Usuário |
| RF07 | Sistema deve permitir consultar o histórico de Interações de um Cliente em ordem cronológica | Média | Usuário |
| RF08 | Sistema deve permitir que um Cliente tenha múltiplos Orçamentos ao longo do tempo | Média | Usuário |
| RF09 | Sistema deve validar Telefone e Email do Cliente no formato correto antes de persistir | Alta | Usuário |
| RF10 | Sistema deve permitir que um Administrador gerencie outros Usuários do sistema | Baixa | Administrador |

## Requisitos não funcionais (RNF)

| ID | Descrição | Prioridade | Ator/Origem |
|----|-----------|------------|-------------|
| RNF01 | Desempenho: o painel Kanban deve carregar em < 2s com até 500 orçamentos ativos | Alta | Equipe |
| RNF02 | Usabilidade: mover um Orçamento entre estágios deve ser feito por drag-and-drop, sem recarregar a página | Alta | Equipe |
| RNF03 | Manutenibilidade: regras de negócio (transições de estágio, cálculo de métricas) devem ser isoláveis de FastAPI e Next.js (Clean Architecture) | Alta | Equipe |
| RNF04 | Confiabilidade: nenhuma transição de estágio inconsistente deve ser persistida, mesmo sob falha parcial (validação no domínio, não só na UI) | Alta | Equipe |
| RNF05 | Portabilidade: tipagem estrita de ponta a ponta (Pydantic no backend, TypeScript no frontend), sem uso de tipos genéricos (`any`) | Média | Equipe |
| RNF06 | Escalabilidade: cada Caso de Uso deve depender apenas de interfaces de repositório, permitindo troca de implementação sem alterar regra de negócio | Média | Equipe |

## Rastreabilidade
Cada RF vira candidato a caso de uso em [03-casos-de-uso.md](03-casos-de-uso.md). RNF03, RNF04 e RNF06 orientam diretamente a arquitetura descrita em [13-implantacao-ddd-clean-tdd.md](13-implantacao-ddd-clean-tdd.md); RNF05 orienta a tipagem das entidades e schemas ([04-diagrama-classes.md](04-diagrama-classes.md)); RF09 origina os Value Objects `Telefone` e `Email`.

## Critérios de aceitação
- Um novo contato registrado aparece imediatamente na coluna "Novo Contato" do Kanban.
- Telefone e e-mail em formato inválido impedem a persistência do Cliente e retornam mensagem de correção.
- Arrastar um card para "Fechado" sem valor definido é rejeitado e o card volta ao estágio original.
- O salto direto de "Novo Contato" para "Fechado" é rejeitado pelo domínio, não apenas pela interface.
- "Perdido" é alcançável a partir de qualquer estágio ativo.
- A linha do tempo de um Cliente exibe as Interações em ordem cronológica, agrupadas por Orçamento.
- As métricas de orçamentos em aberto e taxa de fechamento são calculadas sem consulta ao banco na camada de domínio.
- O painel carrega em menos de 2 segundos com 500 orçamentos ativos.
