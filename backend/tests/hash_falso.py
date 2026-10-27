class HashFalso:
    """Hash de senha previsível e instantâneo para testes de unidade (o real é o scrypt)."""

    def gerar(self, senha: str) -> str:
        return f"hash:{senha}"

    def confere(self, senha: str, hash_guardado: str) -> bool:
        return hash_guardado == f"hash:{senha}"
