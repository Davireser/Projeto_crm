import { sair } from "@/app/login/actions";
import { BotaoSair } from "@/components/sessao/botao-sair";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { rotuloDoPerfil } from "@/domain/entities/usuario";
import { usuarioAtual } from "@/lib/sessao/servidor";

import { LinkNav } from "./link-nav";

const iniciais = (nome: string) =>
  nome
    .split(/\s+/)
    .slice(0, 2)
    .map((parte) => parte[0]?.toUpperCase() ?? "")
    .join("");

/** Parte do cabeçalho que depende de quem está logado (lida a cada requisição). */
export async function MenuUsuario() {
  const usuario = await usuarioAtual();

  return (
    <div className="flex items-center gap-2">
      {usuario.podeGerenciarUsuarios() && <LinkNav href="/usuarios">Usuários</LinkNav>}
      <DropdownMenu>
        <DropdownMenuTrigger asChild>
          <Button variant="ghost" className="gap-2 px-2" aria-label={`Conta de ${usuario.nome}`}>
            <Avatar className="size-7">
              <AvatarFallback className="text-xs">{iniciais(usuario.nome)}</AvatarFallback>
            </Avatar>
            <span className="hidden text-sm sm:inline">{usuario.nome}</span>
          </Button>
        </DropdownMenuTrigger>
        <DropdownMenuContent align="end" className="w-56">
          <DropdownMenuLabel className="grid">
            <span className="truncate">{usuario.nome}</span>
            <span className="truncate text-xs font-normal text-muted-foreground">{usuario.email}</span>
            <span className="text-xs font-normal text-muted-foreground">
              {rotuloDoPerfil(usuario.perfil)}
            </span>
          </DropdownMenuLabel>
          <DropdownMenuSeparator />
          <BotaoSair sair={sair} />
        </DropdownMenuContent>
      </DropdownMenu>
    </div>
  );
}
