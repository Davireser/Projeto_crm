# Imagens dos Diagramas

Exportações estáticas (PNG ou SVG) dos diagramas Mermaid da pasta `docs/arquitetura`.

Os diagramas são mantidos como código Mermaid dentro dos próprios documentos — o GitHub os renderiza nativamente. Esta pasta guarda apenas as exportações necessárias para entregas em formato que não renderiza Mermaid (PDF, slides, documento impresso).

## Convenção de nomes
Nomear o arquivo pelo assunto do diagrama, não pelo número da seção:

```
casos-de-uso.png
diagrama-classes.png
diagrama-er.png
diagrama-objetos.png
estados-orcamento.png
bce-mover-estagio.png
sequencia-mover-estagio.png
sequencia-registrar-contato.png
sequencia-registrar-interacao.png
atividade-funil-completo.png
atividade-mover-card.png
diagrama-componentes.png
```

## Como exportar
Colar o bloco Mermaid em https://mermaid.live e exportar em PNG, ou usar a CLI:

```bash
npx -y @mermaid-js/mermaid-cli -i entrada.mmd -o saida.png -b transparent
```

Ao alterar um diagrama no Markdown, reexportar a imagem correspondente — imagem desatualizada é pior que imagem ausente.
