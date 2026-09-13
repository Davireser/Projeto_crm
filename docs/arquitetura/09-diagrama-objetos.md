# Diagrama de Objetos

O diagrama de objetos congela um instante do sistema em execução e serve para validar, com instâncias concretas, as multiplicidades declaradas em [04-diagrama-classes.md](04-diagrama-classes.md).

## Cenário
O cliente "Embalagens ABC" está em negociação para um pedido de 500 caixas. Duas interações já foram registradas e o valor ainda não foi definido.

```mermaid
classDiagram
    class clienteABC {
        <<instance>>
        id = "c1a2..."
        nome = "Embalagens ABC"
        telefone = "(35) 99999-0001"
        email = "contato@embalagensabc.com"
        empresa = "Embalagens ABC Ltda"
        tipoEmbalagemInteresse = "Caixa de papelão"
    }
    class orcamento500 {
        <<instance>>
        id = "o7b3..."
        clienteId = "c1a2..."
        estagio = "EM_NEGOCIACAO"
        valor = null
        dataAbertura = 2026-09-01
        dataFechamento = null
    }
    class interacao1 {
        <<instance>>
        tipo = "MENSAGEM"
        conteudo = "Solicitou orçamento de 500 caixas"
        dataHora = 2026-09-01T09:12
    }
    class interacao2 {
        <<instance>>
        tipo = "LIGACAO"
        conteudo = "Negociação de prazo de entrega"
        dataHora = 2026-09-03T14:40
    }

    clienteABC --> orcamento500 : possui
    orcamento500 *-- interacao1 : registra
    orcamento500 *-- interacao2 : registra
```

## O que este diagrama valida

| Verificação | Resultado |
|-------------|-----------|
| `Cliente 1 — 0..* Orcamento` | `clienteABC` tem 1 orçamento — dentro de `0..*` |
| `Orcamento 1 — 0..* Interacao` | `orcamento500` tem 2 interações — dentro de `0..*` |
| Composição Orçamento–Interação | `interacao1` e `interacao2` só existem enquanto `orcamento500` existir |
| `Orcamento --> 0..1 ValorOrcado` | `valor = null` é estado válido; é exatamente o que a guarda `[valorDefinido]` bloqueia |
| Tipos do diagrama de classes | `estagio` é valor do enum; `tipo` é valor de `TipoInteracao` |
| RF03 na prática | `orcamento500` **não** pode ir para FECHADO neste instante |

## Cenário complementar: cliente recorrente (RF08)
O mesmo Cliente com dois Orçamentos em momentos diferentes do funil confirma que a agregação `Cliente 1 — 0..*` não é apenas teórica.

```mermaid
classDiagram
    class clienteABC2 {
        <<instance>>
        nome = "Embalagens ABC"
    }
    class orcamentoJan {
        <<instance>>
        estagio = "FECHADO"
        valor = 4200.00
        dataAbertura = 2026-01-15
        dataFechamento = 2026-02-02
    }
    class orcamentoSet {
        <<instance>>
        estagio = "EM_NEGOCIACAO"
        valor = null
        dataAbertura = 2026-09-01
    }

    clienteABC2 --> orcamentoJan : possui
    clienteABC2 --> orcamentoSet : possui
```

`orcamentoJan` demonstra o estado terminal coerente: estágio FECHADO **com** `valor` preenchido e `dataFechamento` definida — o oposto do que RF03 proíbe.
