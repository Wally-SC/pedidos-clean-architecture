"""Portas: contratos que a camada de aplicação exige do mundo externo.

A aplicação depende destas abstrações; a infraestrutura as implementa.
(Dependências apontam sempre para dentro.)
"""

from __future__ import annotations

from typing import Protocol

from pedidos.domain.pedido import Pedido


class RepositorioPedidos(Protocol):
    def salvar(self, pedido: Pedido) -> None: ...

    def obter(self, id_: str) -> Pedido:
        """Levanta PedidoNaoEncontrado se não existir."""
        ...


class Estoque(Protocol):
    def reservar(self, sku: str, quantidade: int) -> None:
        """Levanta EstoqueInsuficiente se não houver saldo."""
        ...

    def liberar(self, sku: str, quantidade: int) -> None: ...
