# Diagrama de Sequência

Os fluxos abaixo detalham a colaboração entre as classes de fronteira, controle e entidade mapeadas em [11-boundary-control-entity.md](11-boundary-control-entity.md).

## UC03 — Mover Estágio do Orçamento

Caso mais crítico do sistema: envolve guarda de negócio, e é onde RNF04 se manifesta na prática.

```mermaid
sequenceDiagram
    actor Usuario
    participant B as PainelKanbanView «boundary»
    participant C as MoverEstagioUseCase «control»
    participant E as Orcamento «entity»
    participant R as OrcamentoRepository

    Usuario ->> B: arrastar card para novo estágio
    B ->> C: moverEstagio(orcamentoId, novoEstagio)
    C ->> R: buscarPorId(orcamentoId)
    R -->> C: orcamento
    C ->> E: moverEstagio(novoEstagio)
    alt transição válida
        E -->> C: estagio atualizado
        C ->> R: salvar(orcamento)
        R -->> C: ok
        C -->> B: sucesso
    else transição inválida (ex: valor não definido)
        E -->> C: exceção TransicaoInvalida
        C -->> B: erro
    end
    B -->> Usuario: atualiza painel
```

**Leitura:** o Use Case não decide nada sobre a transição — ele apenas carrega o agregado, delega a decisão à entidade e persiste se a entidade aceitar. A regra fica testável sem banco e sem FastAPI (RNF03).

## UC01 — Registrar Novo Contato

```mermaid
sequenceDiagram
    actor Usuario
    participant B as ClienteFormView «boundary»
    participant C as RegistrarNovoContatoUseCase «control»
    participant VO as Telefone / Email «value object»
    participant E1 as Cliente «entity»
    participant E2 as Orcamento «entity»
    participant R1 as ClienteRepository
    participant R2 as OrcamentoRepository

    Usuario ->> B: preencher nome, telefone, email, interesse
    B ->> C: registrarNovoContato(dados)
    C ->> VO: criar(telefone), criar(email)
    alt formato válido
        VO -->> C: value objects válidos
        C ->> E1: novo Cliente(nome, telefone, email, empresa, interesse)
        C ->> R1: salvar(cliente)
        R1 -->> C: cliente persistido
        C ->> E2: novo Orcamento(clienteId, NOVO_CONTATO)
        C ->> R2: salvar(orcamento)
        R2 -->> C: orcamento persistido
        C -->> B: sucesso(clienteId, orcamentoId)
    else formato inválido
        VO -->> C: exceção FormatoInvalido
        C -->> B: erro de validação
    end
    B -->> Usuario: exibe card em "Novo Contato" ou mensagem de correção
```

**Leitura:** a validação de RF09 acontece na construção dos Value Objects, antes de qualquer escrita. Se o telefone é inválido, nem o Cliente nem o Orçamento chegam a ser criados — não existe estado parcial.

## UC06 — Registrar Interação

```mermaid
sequenceDiagram
    actor Usuario
    participant B as InteracaoFormView «boundary»
    participant C as RegistrarInteracaoUseCase «control»
    participant E1 as Orcamento «entity»
    participant E2 as Interacao «entity»
    participant R as OrcamentoRepository

    Usuario ->> B: escolher tipo e descrever conteúdo
    B ->> C: registrarInteracao(orcamentoId, tipo, conteudo)
    C ->> R: buscarPorId(orcamentoId)
    R -->> C: orcamento
    C ->> E2: nova Interacao(tipo, conteudo, agora)
    C ->> E1: registrarInteracao(interacao)
    E1 -->> C: interação anexada ao agregado
    C ->> R: salvar(orcamento)
    R -->> C: ok
    C -->> B: sucesso
    B -->> Usuario: exibe interação na linha do tempo
```

**Leitura:** a Interação é criada e anexada **através** do Orçamento, nunca persistida de forma independente. Isso preserva a composição do agregado — não existe `InteracaoRepository`.
