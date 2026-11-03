import type { Metadata, Viewport } from "next";
import { Geist, Geist_Mono } from "next/font/google";

import { Toaster } from "@/components/ui/sonner";
import { ProvedorApi } from "@/lib/api/api-navegador";
import { ProvedorQuery } from "@/lib/query/provedor-query";

import "./globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: {
    template: "%s · CRM de Orçamentos",
    default: "CRM de Atendimento e Orçamentos",
  },
  description:
    "Funil de atendimento e orçamentos: do primeiro contato ao fechamento, com histórico de interações e métricas.",
  applicationName: "CRM de Orçamentos",
  // Área interna de uma empresa: nada aqui deve aparecer em buscadores.
  robots: { index: false, follow: false },
};

export const viewport: Viewport = {
  themeColor: [
    { media: "(prefers-color-scheme: light)", color: "#ffffff" },
    { media: "(prefers-color-scheme: dark)", color: "#0a0a0a" },
  ],
};

export default function RootLayout({ children }: LayoutProps<"/">) {
  return (
    <html lang="pt-BR" className={`${geistSans.variable} ${geistMono.variable} h-full antialiased`}>
      <body className="flex min-h-full flex-col">
        <ProvedorQuery>
          <ProvedorApi>{children}</ProvedorApi>
        </ProvedorQuery>
        <Toaster richColors position="top-right" />
      </body>
    </html>
  );
}
