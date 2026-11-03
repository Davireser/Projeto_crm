import react from "@vitejs/plugin-react";
import { defineConfig } from "vitest/config";

// Dois projetos: "unit" (domínio e aplicação, TypeScript puro em Node) e
// "ui" (componentes com React Testing Library em jsdom).
export default defineConfig({
  plugins: [react()],
  resolve: { tsconfigPaths: true },
  test: {
    projects: [
      {
        extends: true,
        test: {
          name: "unit",
          environment: "node",
          include: ["tests/unit/**/*.test.ts", "tests/arquitetura/**/*.test.ts"],
        },
      },
      {
        extends: true,
        test: {
          name: "ui",
          environment: "jsdom",
          include: ["tests/ui/**/*.test.tsx"],
          setupFiles: ["tests/ui/setup.ts"],
        },
      },
    ],
    coverage: {
      provider: "v8",
      include: ["src/**/*.{ts,tsx}"],
      exclude: [
        "src/**/*.d.ts",
        // Componentes gerados pelo shadcn/ui.
        "src/components/ui/**",
        // Ligação com o Next (páginas, layouts, rotas, proxy e Server Components
        // assíncronos): o Vitest não roda Server Components async. A lógica deles
        // fica em módulos puros testados (lib/sessao/*, application/*).
        "src/app/**",
        "src/proxy.ts",
        "src/lib/config.ts",
        "src/lib/sessao/servidor.ts",
        "src/components/layout/menu-usuario.tsx",
        // Dublês de teste.
        "src/infra/memoria/**",
      ],
      reporter: ["text", "html"],
      thresholds: { lines: 80, branches: 80, functions: 80, statements: 80 },
    },
  },
});
