from __future__ import annotations

from pedidos.domain.excecoes import EstoqueInsuficiente


class EstoqueEmMemoria:
    def __init__(self, saldos: dict[str, int] | None = None) -> None:
        self._saldos = dict(saldos or {})

    def saldo(self, sku: str) -> int:
        return self._saldos.get(sku, 0)

    def reservar(self, sku: str, quantidade: int) -> None:
        disponivel = self.saldo(sku)
        if quantidade > disponivel:
            raise EstoqueInsuficiente(sku, quantidade, disponivel)
        self._saldos[sku] = disponivel - quantidade

    def liberar(self, sku: str, quantidade: int) -> None:
        self._saldos[sku] = self.saldo(sku) + quantidade
