# Requisitos Não Funcionais

Detalhamento dos RNFs tabelados em [../arquitetura/02-requisitos-crm.md](../arquitetura/02-requisitos-crm.md).

## RNF01 - Desempenho do painel
O painel Kanban deve carregar em menos de 2 segundos com até 500 orçamentos ativos. O endpoint do painel retorna uma projeção enxuta do Orçamento, sem carregar as interações; o detalhe do card é buscado sob demanda.

**Prioridade:** Alta · **Verificação:** teste de carga com 500 registros medindo o tempo de resposta.

## RNF02 - Usabilidade do funil
Mover um Orçamento entre estágios deve ser feito por drag-and-drop, sem recarregar a página. A interface aplica atualização otimista e desfaz a movimentação quando o domínio rejeita a transição, exibindo o motivo.

**Prioridade:** Alta · **Verificação:** teste de frontend do arraste, incluindo o caminho de rollback.

## RNF03 - Manutenibilidade e independência de framework
As regras de negócio — transições de estágio, guardas de valor e cálculo de métricas — devem ser isoláveis de FastAPI e Next.js. Nenhum import de `fastapi`, `sqlalchemy` ou `pydantic` pode existir em `domain/` ou `application/`.

**Prioridade:** Alta · **Verificação:** teste automatizado de arquitetura que falha a build ao detectar import proibido.

## RNF04 - Confiabilidade das transições
Nenhuma transição de estágio inconsistente pode ser persistida, mesmo sob falha parcial. A validação acontece na entidade antes de qualquer chamada ao repositório, de modo que uma rejeição nunca deixa estado intermediário no banco.

**Prioridade:** Alta · **Verificação:** testes de unidade que confirmam que `salvar()` não é chamado em caso de rejeição.

## RNF05 - Tipagem estrita de ponta a ponta
O sistema deve manter tipagem estrita em toda a cadeia: Pydantic no backend, TypeScript no frontend, sem uso de `any` nem de tipos genéricos que anulem a checagem. Os tipos do frontend espelham os schemas de saída da API.

**Prioridade:** Média · **Verificação:** `mypy --strict` no backend e `tsc --noEmit` com `noImplicitAny` no frontend, ambos em CI.

## RNF06 - Escalabilidade por inversão de dependência
Cada Caso de Uso deve depender apenas de interfaces de repositório, permitindo trocar a implementação de persistência sem alterar regra de negócio. Um repositório fake in-memory deve ser suficiente para exercitar todos os use cases.

**Prioridade:** Média · **Verificação:** todos os testes de use case rodam sem banco.

## RNF07 - Segurança do acesso
As rotas do CRM devem exigir autenticação; as operações de gestão de usuários exigem perfil de Administrador. Senhas são armazenadas apenas como hash.

**Prioridade:** Alta · **Verificação:** teste de integração cobrindo acesso não autenticado e acesso com perfil insuficiente.

## RNF08 - Integridade de dados
O banco deve preservar a composição entre Orçamento e Interação (`ON DELETE CASCADE`) e impedir a exclusão de Cliente com histórico (`ON DELETE RESTRICT`). O conjunto de estágios é restrito por CHECK.

**Prioridade:** Alta · **Verificação:** teste de integração dos repositórios contra banco de teste.

## RNF09 - Portabilidade
A aplicação deve funcionar em navegadores modernos de desktop e mobile, sem dependência de aplicativo nativo. O backend deve subir por Docker Compose em qualquer ambiente com Docker.

**Prioridade:** Média · **Verificação:** execução limpa a partir de `docker compose up` em máquina sem dependências instaladas.

## RNF10 - Rastreabilidade da documentação
Todo requisito funcional deve estar ligado a pelo menos um caso de uso e a pelo menos um teste, e essa ligação deve estar registrada nas tabelas de rastreabilidade de [../arquitetura/13-implantacao-ddd-clean-tdd.md](../arquitetura/13-implantacao-ddd-clean-tdd.md).

**Prioridade:** Média · **Verificação:** revisão das tabelas de rastreabilidade a cada entrega.
