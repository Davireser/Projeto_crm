import type { MetadataRoute } from "next";

/** Permite instalar o CRM como aplicativo; abre direto no painel. */
export default function manifest(): MetadataRoute.Manifest {
  return {
    name: "CRM de Atendimento e Orçamentos",
    short_name: "CRM Orçamentos",
    description: "Funil de atendimento e orçamentos: do primeiro contato ao fechamento.",
    lang: "pt-BR",
    start_url: "/painel",
    display: "standalone",
    background_color: "#ffffff",
    theme_color: "#ffffff",
    icons: [{ src: "/icon.svg", sizes: "any", type: "image/svg+xml" }],
  };
}
