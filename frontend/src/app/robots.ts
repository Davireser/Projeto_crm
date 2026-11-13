import type { MetadataRoute } from "next";

/** Área interna de uma empresa: nenhum buscador deve indexar (combina com o `robots` do layout). */
export default function robots(): MetadataRoute.Robots {
  return { rules: { userAgent: "*", disallow: "/" } };
}
