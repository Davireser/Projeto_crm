# Visão do Produto

## Objetivo
Desenvolver um CRM de Atendimento e Orçamentos para pequenos negócios que vendem por contato direto — WhatsApp, ligação e indicação — como uma empresa de embalagens. O objetivo é organizar o funil de atendimento em um painel visual, registrar o histórico de cada negociação e garantir consistência das transições de estágio na camada de domínio.

A plataforma funciona como um organizador de funil: cada contato vira um Cliente com um Orçamento associado, e esse Orçamento percorre estágios controlados até fechar ou ser perdido.

## Público-alvo
- donos de pequenos negócios que atendem por contato direto e perdem oportunidades por falta de controle;
- atendentes que precisam retomar uma negociação sabendo o que já foi conversado;
- gestores que querem enxergar quantos orçamentos estão em aberto e qual a taxa de fechamento;
- administradores responsáveis por gerenciar os usuários do sistema.

## Problema resolvido
Negócios que vendem por contato direto controlam atendimento em caderno, planilha ou na própria conversa do WhatsApp. O resultado é previsível: orçamento esquecido, cliente sem retorno, ausência de histórico e nenhuma noção de quanto está em aberto.

Um CRM comercial completo resolve isso, mas traz complexidade, custo e campos que o negócio não usa. O que falta é um funil enxuto, com poucas etapas bem definidas e regras que impeçam estados inconsistentes.

## Solução proposta
O CRM centraliza o atendimento em um painel Kanban com cinco estágios:
- **Novo Contato** — a oportunidade acabou de entrar;
- **Em Negociação** — há conversa ativa com o cliente;
- **Orçamento Enviado** — valor definido e proposta entregue;
- **Fechado** — venda concretizada;
- **Perdido** — oportunidade encerrada sem venda.

Cada Orçamento acumula Interações (mensagem, ligação, reunião) que compõem a linha do tempo do Cliente. As métricas do funil ficam no topo do painel.

## Fluxos principais
### 1. Registro de novo contato
- o usuário informa nome, telefone, e-mail e tipo de embalagem de interesse;
- o sistema valida telefone e e-mail antes de persistir;
- o sistema cria o Cliente e abre um Orçamento em "Novo Contato".

### 2. Condução do funil
- o usuário arrasta o card do Orçamento para o próximo estágio;
- o domínio valida a transição e a existência de valor quando exigido;
- transições inválidas são rejeitadas e o estágio atual é mantido.

### 3. Registro de interação
- o usuário escolhe o tipo (mensagem, ligação, reunião) e descreve o conteúdo;
- o sistema associa a Interação ao Orçamento com data e hora;
- a Interação passa a compor o histórico cronológico do Cliente.

### 4. Acompanhamento de métricas
- o painel exibe a quantidade de orçamentos em aberto;
- o painel exibe a taxa de fechamento do funil.

## Principais restrições
- não haverá integração oficial com a API do WhatsApp Business — o contato continua manual;
- não haverá emissão fiscal, cobrança ou gateway de pagamento;
- não haverá catálogo de produtos, controle de estoque ou logística;
- não haverá portal de autoatendimento para o cliente final;
- a validação das transições de estágio ocorre no domínio, não apenas na interface (RNF04);
- as regras de negócio não podem depender de FastAPI nem de Next.js (RNF03).
