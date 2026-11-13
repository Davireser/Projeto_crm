import { describe, expect, it } from "vitest";

import manifest from "@/app/manifest";
import robots from "@/app/robots";

describe("SEO de uma área interna", () => {
  it("robots.txt pede para nenhum buscador indexar o CRM", () => {
    expect(robots().rules).toEqual({ userAgent: "*", disallow: "/" });
  });

  it("manifest abre direto no painel, em português, com o ícone do app", () => {
    const m = manifest();

    expect(m).toMatchObject({ name: "CRM de Atendimento e Orçamentos", lang: "pt-BR", start_url: "/painel" });
    expect(m.icons).toContainEqual(expect.objectContaining({ src: "/icon.svg", type: "image/svg+xml" }));
  });
});
