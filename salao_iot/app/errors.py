"""Erros de negócio. O main.py converte cada um em uma resposta HTTP."""


class NaoEncontrado(Exception):
    """Zona ou pedido inexistente (HTTP 404)."""


class RegraDeNegocio(Exception):
    """Ação inválida para o estado atual (HTTP 409)."""
