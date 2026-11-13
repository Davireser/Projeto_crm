# Imagem do frontend (Next.js com output "standalone"). Quem monta e sobe é o
# docker-compose.yml da raiz do projeto, no serviço "frontend".

FROM node:24-alpine AS base
ENV NEXT_TELEMETRY_DISABLED=1
WORKDIR /app


# Dependências antes do código: esta camada só é refeita quando o package-lock.json muda.
FROM base AS dependencias
COPY package.json package-lock.json ./
RUN npm ci


FROM base AS build
COPY --from=dependencias /app/node_modules ./node_modules
COPY . .
RUN npm run build


# Só o servidor gerado pelo build (sem node_modules completo), rodando sem root.
FROM base AS app
ENV NODE_ENV=production \
    PORT=3000 \
    HOSTNAME=0.0.0.0
COPY --from=build --chown=node:node /app/.next/standalone ./
COPY --from=build --chown=node:node /app/.next/static ./.next/static
COPY --from=build --chown=node:node /app/public ./public
USER node
EXPOSE 3000
CMD ["node", "server.js"]
