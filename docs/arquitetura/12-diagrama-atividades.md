# Diagrama de Atividades

## Fluxo principal — do primeiro contato ao fechamento ou perda

Processo ponta a ponta do negócio, atravessando UC01, UC03, UC05 e UC06.

```mermaid
flowchart TD
    Start((Início)) --> A1[Usuário registra novo contato]
    A1 --> D0{Telefone e email válidos?}
    D0 -- Não --> A0[Sistema solicita correção]
    A0 --> A1
    D0 -- Sim --> A2[Orçamento criado em Novo Contato]
    A2 --> A3[Usuário registra interações]
    A3 --> D1{Cliente segue negociando?}
    D1 -- Não --> A8[Marcar Perdido]
    D1 -- Sim --> A4[Mover para Em Negociação]
    A4 --> A5[Definir valor do orçamento]
    A5 --> A6[Mover para Orçamento Enviado]
    A6 --> D2{Cliente aceita?}
    D2 -- Não --> A8
    D2 -- Sim --> A7[Mover para Fechado]
    A7 --> End((Fim))
    A8 --> End
```

## Fluxo detalhado — movimentação de card no Kanban (UC03)

Mostra o tratamento de erro exigido por RNF02 (sem recarregar a página) e RNF04 (rejeição no domínio).

```mermaid
flowchart TD
    S((Início)) --> B1[Usuário arrasta card para nova coluna]
    B1 --> B2[Interface atualiza posição de forma otimista]
    B2 --> B3[Frontend envia PATCH do estágio]
    B3 --> B4[Use Case carrega o Orçamento]
    B4 --> C1{Transição permitida pela máquina de estados?}
    C1 -- Não --> B7[Domínio lança TransicaoInvalida]
    C1 -- Sim --> C2{Destino exige valor definido?}
    C2 -- Não --> B5[Atualizar estágio]
    C2 -- Sim --> C3{Valor já definido?}
    C3 -- Sim --> B5
    C3 -- Não --> B7
    B5 --> B6[Repositório persiste o Orçamento]
    B6 --> B8[Interface confirma a nova coluna]
    B7 --> B9[Interface devolve o card à coluna de origem e exibe o motivo]
    B8 --> E((Fim))
    B9 --> E
```

## Raias por responsabilidade

```mermaid
flowchart TB
    subgraph Usuario["Usuário"]
        U1[Arrastar card]
        U2[Ler mensagem de erro]
    end
    subgraph Frontend["Frontend (boundary)"]
        F1[Atualização otimista]
        F2[Chamada HTTP]
        F3[Rollback visual]
    end
    subgraph Backend["Use Case (control)"]
        C1[Carregar agregado]
        C2[Persistir se aceito]
    end
    subgraph Dominio["Orçamento (entity)"]
        D1[Validar transição]
        D2[Validar guarda de valor]
    end

    U1 --> F1 --> F2 --> C1 --> D1 --> D2
    D2 -->|aceito| C2
    D2 -->|rejeitado| F3 --> U2
```

## Pontos de decisão relevantes

| Decisão | Onde é tomada | Requisito |
|---------|---------------|-----------|
| Telefone e e-mail válidos? | Value Objects `Telefone` e `Email`, na construção | RF09 |
| Transição permitida? | `Orcamento.moverEstagio()` | RF02 |
| Valor definido? | Guarda `[valorDefinido]` em `Orcamento.moverEstagio()` | RF03 |
| Cliente segue negociando? | Usuário — decisão de negócio, não do sistema | — |
| Cliente aceita? | Usuário — decisão de negócio, não do sistema | — |

Nenhuma decisão de negócio é tomada pelo frontend. Ele apenas antecipa o resultado provável para não travar a interface, e desfaz quando o domínio discorda.
