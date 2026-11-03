/**
 * Teste de arquitetura (RNF03): as dependências apontam para dentro.
 *
 * - domain: TypeScript puro; só importa o próprio domínio.
 * - application: só importa domain e application.
 */
import { readdirSync, readFileSync, statSync } from "node:fs";
import { join, relative, resolve } from "node:path";
import { describe, expect, it } from "vitest";

const SRC = resolve(__dirname, "../../src");
const IMPORT = /(?:import|export)\s[^"']*?from\s+["']([^"']+)["']|import\(\s*["']([^"']+)["']\s*\)/g;

function arquivos(pasta: string): string[] {
  return readdirSync(pasta).flatMap((nome) => {
    const caminho = join(pasta, nome);
    return statSync(caminho).isDirectory() ? arquivos(caminho) : [caminho];
  });
}

function importsDe(arquivo: string): string[] {
  const codigo = readFileSync(arquivo, "utf-8");
  return [...codigo.matchAll(IMPORT)].map((m) => m[1] ?? m[2] ?? "");
}

function camadaDoImport(arquivo: string, especificador: string): string {
  if (especificador.startsWith("@/")) return especificador.slice(2).split("/")[0] ?? "";
  if (especificador.startsWith(".")) {
    const destino = relative(SRC, resolve(arquivo, "..", especificador));
    return destino.split(/[\\/]/)[0] ?? "";
  }
  return `pacote:${especificador}`;
}

function violacoes(camada: string, permitidas: string[]): string[] {
  return arquivos(join(SRC, camada)).flatMap((arquivo) =>
    importsDe(arquivo)
      .filter((imp) => !permitidas.includes(camadaDoImport(arquivo, imp)))
      .map((imp) => `${relative(SRC, arquivo)} importa "${imp}"`),
  );
}

describe("arquitetura em camadas", () => {
  it("domain não depende de framework nem de outras camadas", () => {
    expect(violacoes("domain", ["domain"])).toEqual([]);
  });

  it("application depende só de domain", () => {
    expect(violacoes("application", ["domain", "application"])).toEqual([]);
  });
});
