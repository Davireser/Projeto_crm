# Requisitos Funcionais

Detalhamento dos RFs tabelados em [../arquitetura/02-requisitos-crm.md](../arquitetura/02-requisitos-crm.md).

## RF01 - Registrar novo contato
O sistema deve permitir que o Usuário registre um novo contato informando nome, telefone, e-mail, empresa e tipo de embalagem de interesse. Ao concluir, o sistema cria um Cliente e abre automaticamente um Orçamento no estágio "Novo Contato" vinculado a ele.

**Prioridade:** Alta · **Ator:** Usuário · **Caso de uso:** UC01

## RF02 - Mover estágio do orçamento
O sistema deve permitir mover um Orçamento entre estágios respeitando a sequência Novo Contato → Em Negociação → Orçamento Enviado → Fechado. O estágio "Perdido" é alcançável a partir de qualquer estágio ativo. Saltos de etapa e retrocessos são rejeitados.

**Prioridade:** Alta · **Ator:** Usuário · **Caso de uso:** UC03

## RF03 - Impedir fechamento sem valor definido
O sistema deve impedir que um Orçamento seja movido para "Orçamento Enviado" ou "Fechado" enquanto não houver um valor definido. A validação ocorre na entidade de domínio, não apenas na interface.

**Prioridade:** Alta · **Ator:** Usuário · **Caso de uso:** UC03, UC05

## RF04 - Registrar interação
O sistema deve permitir registrar uma Interação vinculada a um Orçamento, escolhendo entre os tipos mensagem, ligação e reunião, com descrição do conteúdo. A data e hora são atribuídas pelo sistema no momento do registro.

**Prioridade:** Alta · **Ator:** Usuário · **Caso de uso:** UC06

## RF05 - Exibir painel Kanban
O sistema deve exibir um painel com os Orçamentos organizados em colunas por estágio, permitindo visualizar de imediato a distribuição do funil.

**Prioridade:** Alta · **Ator:** Usuário · **Caso de uso:** UC07

## RF06 - Calcular métricas do funil
O sistema deve calcular e exibir a quantidade de orçamentos em aberto e a taxa de fechamento do funil.

**Prioridade:** Média · **Ator:** Usuário · **Caso de uso:** UC08

## RF07 - Consultar histórico de interações do cliente
O sistema deve permitir consultar todas as Interações de um Cliente em ordem cronológica, reunindo os registros de todos os seus Orçamentos.

**Prioridade:** Média · **Ator:** Usuário · **Caso de uso:** UC09

## RF08 - Permitir múltiplos orçamentos por cliente
O sistema deve permitir que um mesmo Cliente acumule vários Orçamentos ao longo do tempo, em estágios independentes entre si, preservando o histórico de negociações anteriores.

**Prioridade:** Média · **Ator:** Usuário · **Caso de uso:** UC01, UC09

## RF09 - Validar telefone e e-mail do cliente
O sistema deve validar o formato do telefone e do e-mail antes de persistir o Cliente. Dados em formato inválido impedem a criação do registro e retornam mensagem de correção.

**Prioridade:** Alta · **Ator:** Usuário · **Caso de uso:** UC02

## RF10 - Gerenciar usuários do sistema
O sistema deve permitir que um Administrador crie, edite e desative outros Usuários. Um Administrador não pode desativar a própria conta.

**Prioridade:** Baixa · **Ator:** Administrador · **Caso de uso:** UC10
