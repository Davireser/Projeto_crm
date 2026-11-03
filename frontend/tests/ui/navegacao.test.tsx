import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import { LinkNav } from "@/components/layout/link-nav";

vi.mock("next/navigation", () => ({ usePathname: () => "/clientes/abc" }));

describe("LinkNav", () => {
  it("marca a seção atual com aria-current", () => {
    render(
      <nav>
        <LinkNav href="/painel">Painel</LinkNav>
        <LinkNav href="/clientes">Clientes</LinkNav>
      </nav>,
    );

    expect(screen.getByRole("link", { name: "Clientes" })).toHaveAttribute("aria-current", "page");
    expect(screen.getByRole("link", { name: "Painel" })).not.toHaveAttribute("aria-current");
  });
});
