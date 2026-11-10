# Plano do Frontend — CRM de Atendimento e Orçamentos

Status: **aprovado** (2026-11-03). Atualizado ao final de cada parte.

| Parte | Situação |
|-------|----------|
| F1 — projeto + domínio | ✅ Next 16.4.5, React 19.3, Vitest 5.1, Node 26 LTS. Domínio: `Email`, `Telefone`, `ValorOrcado` (centavos inteiros), estágios/tipos, `Funil`, `Orcamento`, `Interacao`, `Cliente`, `NovoContato`, `Usuario`/`NovoUsuario`, `MetricasFunil`. Teste de arquitetura ativo. |
| F2 — aplicação + infra | ✅ Portas, 8 casos de uso, `ClienteHttp` (erro padrão da API → `ErroRemoto`), DTOs, mapeadores, gateways HTTP e em memória. 97 testes, cobertura de linhas 99,7%; `tsc` e `eslint` limpos. |
| F3 — sessão + layout | ✅ shadcn/ui (Radix). Login por Server Action → JWT em cookie httpOnly; `proxy.ts` com checagem otimista (`decidirAcesso`); repasse `/api/[...caminho]` → backend com o token; layout com menu, usuário e Sair (limpa o cache offline); TanStack Query com cache persistido. Páginas F4–F6 como "em construção". `next build`: páginas em Partial Prerender. |
| F4 — painel Kanban | ✅ Página `/painel` renderizada no servidor com os dados (Suspense + esqueleto) e hidratada no TanStack Query. Cinco colunas, arraste por mouse e teclado (@dnd-kit, avisos em português), colunas destacam destino válido/inválido pelo `Funil` (RN01/RN02), movimento otimista com rollback e toast (RNF02). Gaveta de detalhe: mover, definir valor, registrar interação. Busca sem acento. Offline: cache persistido; alterações pausam sem rede e são enviadas quando volta (indicador de status); 401 leva ao login. 164 testes, branches 87,7%. |
| F5 — contatos e clientes | ✅ `/contatos/novo`: o domínio valida antes da API e mostra todos os erros juntos, cada um no seu campo (RF09); erro da API com `campo` também vai para o campo; o card entra no painel em cache; sem rede, o envio fica pausado com aviso. `/clientes/[id]`: Server Component com `generateMetadata` (nome do cliente) e busca única por requisição (`cache`), contato, orçamentos e linha do tempo das interações, mais recentes primeiro (RF07, RF08); 404/422 → página "Cliente não encontrado". Correção: `GET /orcamentos` vem agrupado por estágio; o card agora traz `dataFechamento` (backend). 173 testes, branches 88%. |
| F6–F7 | pendentes |

Decisões tomadas durante F1/F2:
- O `Orcamento` do frontend é o card do Kanban (com `clienteNome` e `qtdInteracoes`). Ao alterar, a API devolve só estágio, valor e data de fechamento (`AtualizacaoOrcamento`), e o caso de uso junta isso ao card local.
- Os casos de uso validam no domínio antes de chamar a API: transição inválida, valor inválido e formulário inválido nem saem do navegador.
- `taxaFechamento` chega da API como percentual (`"62.50"`) e é exibida como `62,5%`, ou `—` quando nada foi concluído (RN07).

## Requisitos do professor

1. Domínio rico (Clean Architecture + DDD) com validação e testes unitários em **TypeScript puro**, feito com **TDD**.
2. **Next.js 16+** com App Router, Server e Client Components, otimizações automáticas, **Turbopack**, SEO e Metadata; **TailwindCSS** e **shadcn/ui**; **TanStack Query** com *offline first* quando fizer sentido.
3. **Vitest** + **React Testing Library**: testes unitários e de interface.

Requisitos do projeto que o frontend cobre: RF01–RF10 (telas), RNF02 (arraste com atualização otimista e rollback), RNF03 (domínio sem framework), RNF05 (TypeScript estrito, sem `any`), RNF07 (rotas protegidas por perfil).

## Stack

| Item | Escolha |
|------|---------|
| Framework | Next.js 16 (App Router, Turbopack no `dev` e no `build`) + React 19 |
| Linguagem | TypeScript `strict` + `noUncheckedIndexedAccess`, sem `any` (ESLint bloqueia) |
| Estilo | Tailwind CSS v4 + shadcn/ui (Radix) + lucide-react |
| Dados | TanStack Query v5 com `networkMode: "offlineFirst"` e cache persistido (`persistQueryClient` + localStorage) |
| Formulários | react-hook-form + zod **só na borda**; quem valida de verdade é o domínio |
| Drag-and-drop | dnd-kit (acessível por teclado) |
| Testes | Vitest + React Testing Library + jsdom + @vitest/coverage-v8 (mínimo 80%) |
| Qualidade | ESLint (next/core-web-vitals + typescript strict), Prettier, `tsc --noEmit` |

## Arquitetura (`frontend/src/`)

```
src/
  domain/          TypeScript puro: entidades, value objects, erros, regras. Sem React/Next/fetch.
    value-objects/ Email, Telefone, ValorOrcado, EstagioAtendimento, TipoInteracao
    entities/      Orcamento, Cliente, Interacao, Usuario
    funil/         MapaDeTransicoes (recebido da API) + regras de movimento
    errors.ts      ErroDominio, FormatoInvalido, TransicaoInvalida
  application/     Casos de uso e portas (interfaces dos gateways). Sem React.
    ports/         OrcamentoGateway, ClienteGateway, AuthGateway, UsuarioGateway, MetricasGateway
    use-cases/     moverEstagio, definirValor, registrarContato, registrarInteracao, ...
  infra/           Implementações: cliente HTTP, mapeadores DTO ⇄ domínio, gateways HTTP e em memória
  app/             Rotas do App Router (Server Components por padrão)
  components/      ui/ (shadcn) e features/ (kanban, clientes, usuarios, metricas)
  hooks/           Hooks do TanStack Query que chamam os casos de uso
  lib/             query-client, providers, utilitários
tests/             unit/ (domínio e aplicação), ui/ (componentes), arquitetura
```

Regras:
- As dependências apontam para dentro: `domain` não importa nada externo e `application` só importa `domain`. Um **teste de arquitetura** (o primeiro a ser escrito) varre os imports e falha se a regra for quebrada.
- **Regras de transição não são duplicadas.** O domínio TS recebe o mapa de `GET /orcamentos/transicoes` e valida o movimento com ele (decisão sujeita a veto, seguindo `especificacoes_tecnicas.md` §“Endpoint de apoio”). A guarda de valor (RN02) usa a mesma informação. O backend continua sendo a autoridade final.
- Os value objects espelham os do backend: e-mail válido, telefone brasileiro com 10 ou 11 dígitos, valor positivo com 2 casas e formatação em BRL.
- Os componentes não chamam `fetch` direto: usam hooks → casos de uso → portas.

## Autenticação e segurança

- O login é feito por uma **Server Action**, que chama `POST /api/v1/auth/login` e grava o JWT num **cookie httpOnly, SameSite=Lax** (Secure em produção). O token nunca fica acessível ao JavaScript do navegador.
- **`proxy.ts`** (antigo middleware, renomeado no Next 16) redireciona para `/login` quem está sem cookie e bloqueia `/usuarios` para quem não é ADMINISTRADOR.
- O navegador fala só com o próprio Next: um Route Handler `/api/[...caminho]` repassa as chamadas para o backend, colocando o `Authorization: Bearer` a partir do cookie. Assim não é preciso CORS e a URL da API fica no servidor (`API_URL`).
- Um 401 vindo do backend limpa o cookie e manda para o login.

## Telas (rotas)

| Rota | Render | Conteúdo | Req. |
|------|--------|----------|------|
| `/login` | Server + form client | Login | RNF07 |
| `/` → `/painel` | Server (dados iniciais) + Client (arraste) | Kanban com 5 colunas, arraste otimista com rollback e motivo, filtro | RF02, RF03, RF05, RNF02 |
| `/contatos/novo` | Client | Registrar cliente + primeiro orçamento | RF01, RF09 |
| `/clientes/[id]` | Server | Dados do cliente, orçamentos e linha do tempo | RF07, RF08 |
| Detalhe do orçamento (drawer no painel) | Client | Definir valor, registrar interação | RF03, RF04 |
| `/metricas` | Server | Indicadores do funil | RF06 |
| `/usuarios` | Server + Client | Listar, criar, editar e ativar/desativar (só ADMINISTRADOR) | RF10 |

**SEO/Metadata:** `metadata` com template de título em todas as rotas, `generateMetadata` em `/clientes/[id]`, `robots.ts` (área logada com noindex), `manifest.ts`, ícone, `lang="pt-BR"` e `next/font`.

**Offline first:**
- Leituras: o cache do TanStack Query é persistido, então o painel abre com os últimos dados mesmo sem rede.
- Escritas: mutações feitas offline ficam pausadas e são reenviadas ao reconectar, com indicador "offline / sincronizando".
- Mover estágio usa atualização otimista; se o backend recusar, a mudança é desfeita e o motivo aparece num toast.

## Metodologia — TDD em partes

No fim de cada parte, `lint`, `tsc` e `vitest` precisam estar verdes, e este plano é atualizado.

| Parte | Entrega | Pronto quando |
|-------|---------|---------------|
| F1 | Projeto Next 16 em `frontend/`, Tailwind, shadcn, Vitest; teste de arquitetura; **domínio** (VOs, entidades, funil) com testes unitários | domínio com 100% de cobertura, sem import de framework |
| F2 | Portas, casos de uso, gateways em memória, cliente HTTP e mapeadores DTO | casos de uso testados com gateways em memória |
| F3 | Login (Server Action + cookie), `proxy.ts`, proxy `/api/[...caminho]`, layout, navegação, providers do TanStack Query | testes de UI do formulário de login e testes do proxy |
| F4 | Painel Kanban: colunas, cards, arraste otimista e rollback, drawer de detalhe (valor e interação), offline | teste de UI do arraste, incluindo o rollback (RNF02) |
| F5 | Novo contato, cliente com linha do tempo | testes de UI de validação e envio |
| F6 | Métricas e usuários (só admin) | testes de UI e de permissão |
| F7 | Metadata/SEO, `Dockerfile` (output standalone) + serviço `frontend` no `docker-compose.yml`, README | `docker compose up` sobe db + api + frontend; cobertura ≥ 80% |

## Ambiente (Windows)

- É preciso ter o **Node.js 22 LTS** (ou mais novo). A máquina tem o Smart App Control ligado, que já bloqueou binários nativos antes. Next (SWC), Tailwind v4 (lightningcss) e Vitest (rollup/esbuild) usam binários nativos, então a primeira coisa da F1 é testar se eles rodam. Se forem bloqueados, o plano B é rodar `npm` dentro de um container `node:22`.
- Comandos em PowerShell, sempre na pasta `frontend`: `npm run dev`, `npm test`, `npm run test:cov`, `npm run lint`.

## Decisões sujeitas a veto

1. Regras de transição vindas da API, não escritas de novo em TS.
2. JWT em cookie httpOnly com proxy no Next, em vez de token no localStorage.
3. Cache persistido em localStorage (dados de CRM de um usuário só; o cache é limpo no logout).
4. npm como gerenciador de pacotes.
