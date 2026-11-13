import "server-only";

/**
 * URL do backend, lida só no servidor (o navegador fala com `/api/...` do Next).
 * No Docker, aponta para o serviço `api`; localmente, para a porta 8000.
 */
export const URL_API = `${(process.env.API_URL ?? "http://localhost:8000").replace(/\/+$/, "")}/api/v1`;

export const EM_PRODUCAO = process.env.NODE_ENV === "production";
