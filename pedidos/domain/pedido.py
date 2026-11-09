from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from pedidos.domain.dinheiro import Dinheiro
from pedidos.domain.excecoes import PedidoNaoEditavel, PedidoVazio, TransicaoInvalida


class StatusPedido(str, Enum):
    RASCUNHO = "rascunho"
    CONFIRMADO = "confirmado"
    CANCELADO = "cancelado"


@dataclass(frozen=True)
class ItemPedido:
    sku: str
    quantidade: int
    preco_unitario: Dinheiro

    def __post_init__(self) -> None:
        if not self.sku.strip():
            raise ValueError("sku não pode ser vazio")
        if self.quantidade <= 0:
            raise ValueError("quantidade deve ser maior que zero")

    @property
    def subtotal(self) -> Dinheiro:
        return self.preco_unitario.vezes(self.quantidade)


class Pedido:
    """Agregado raiz. Toda regra de negócio de pedidos vive aqui, sem depender de infraestrutura."""

    def __init__(
        self,
        id: str,
        itens: list[ItemPedido] | None = None,
        status: StatusPedido = StatusPedido.RASCUNHO,
    ) -> None:
        self.id = id
        self._itens: list[ItemPedido] = list(itens or [])
        self.status = status

    @property
    def itens(self) -> tuple[ItemPedido, ...]:
        return tuple(self._itens)

    @property
    def total(self) -> Dinheiro:
        total = Dinheiro.zero()
        for item in self._itens:
            total = total + item.subtotal
        return total

    def _exigir_rascunho(self) -> None:
        if self.status is not StatusPedido.RASCUNHO:
            raise PedidoNaoEditavel(f"pedido {self.id} está {self.status.value} e não pode ser alterado")

    def adicionar_item(self, sku: str, quantidade: int, preco_unitario: Dinheiro) -> None:
        """Adiciona um item; se o SKU já existe, soma a quantidade (o preço deve ser o mesmo)."""
        self._exigir_rascunho()
        novo = ItemPedido(sku, quantidade, preco_unitario)
        for i, existente in enumerate(self._itens):
            if existente.sku == sku:
                if existente.preco_unitario != preco_unitario:
                    raise ValueError(f"preço diferente para {sku} já presente no pedido")
                self._itens[i] = ItemPedido(sku, existente.quantidade + quantidade, preco_unitario)
                return
        self._itens.append(novo)

    def remover_item(self, sku: str) -> None:
        self._exigir_rascunho()
        restantes = [i for i in self._itens if i.sku != sku]
        if len(restantes) == len(self._itens):
            raise KeyError(f"item {sku} não está no pedido")
        self._itens = restantes

    def confirmar(self) -> None:
        if self.status is not StatusPedido.RASCUNHO:
            raise TransicaoInvalida(f"só é possível confirmar rascunhos (atual: {self.status.value})")
        if not self._itens:
            raise PedidoVazio()
        self.status = StatusPedido.CONFIRMADO

    def cancelar(self) -> None:
        if self.status is StatusPedido.CANCELADO:
            raise TransicaoInvalida("pedido já está cancelado")
        self.status = StatusPedido.CANCELADO
