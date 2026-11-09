from __future__ import annotations

from pedidos.domain.excecoes import PedidoNaoEncontrado
from pedidos.domain.pedido import Pedido


class RepositorioPedidosEmMemoria:
    def __init__(self) -> None:
        self._dados: dict[str, tuple] = {}

    def salvar(self, pedido: Pedido) -> None:
        # guarda um snapshot, para que alterar o objeto depois não mude o "banco"
        self._dados[pedido.id] = (pedido.itens, pedido.status)

    def obter(self, id_: str) -> Pedido:
        try:
            itens, status = self._dados[id_]
        except KeyError:
            raise PedidoNaoEncontrado(id_) from None
        return Pedido(id_, list(itens), status)
