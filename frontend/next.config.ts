import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Gera .next/standalone: servidor mínimo usado pela imagem Docker (frontend/Dockerfile).
  output: "standalone",
  cacheComponents: true,
  partialPrefetching: true,
  turbopack: {
    rules: {
      "*.css": {
        loaders: ["@tailwindcss/turbopack"],
        as: "*.css",
      },
    },
  },
};

export default nextConfig;
