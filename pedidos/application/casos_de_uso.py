from __future__ import annotations

from typing import Callable
from uuid import uuid4

from pedidos.application.portas import Estoque, RepositorioPedidos
from pedidos.domain.dinheiro import Dinheiro
from pedidos.domain.excecoes import ErroDeDominio
from pedidos.domain.pedido import Pedido, StatusPedido


class CriarPedido:
    def __init__(self, repo: RepositorioPedidos, gerar_id: Callable[[], str] = lambda: uuid4().hex) -> None:
        self._repo = repo
        self._gerar_id = gerar_id

    def executar(self) -> Pedido:
        pedido = Pedido(id=self._gerar_id())
        self._repo.salvar(pedido)
        return pedido


class AdicionarItem:
    def __init__(self, repo: RepositorioPedidos) -> None:
        self._repo = repo

    def executar(self, pedido_id: str, sku: str, quantidade: int, preco_unitario: Dinheiro) -> Pedido:
        pedido = self._repo.obter(pedido_id)
        pedido.adicionar_item(sku, quantidade, preco_unitario)
        self._repo.salvar(pedido)
        return pedido


class ConfirmarPedido:
    """Reserva o estoque de todos os itens. Se algum item falhar, desfaz as reservas já feitas."""

    def __init__(self, repo: RepositorioPedidos, estoque: Estoque) -> None:
        self._repo = repo
        self._estoque = estoque

    def executar(self, pedido_id: str) -> Pedido:
        pedido = self._repo.obter(pedido_id)
        pedido.confirmar()  # valida regras de domínio antes de tocar no estoque

        reservados: list[tuple[str, int]] = []
        try:
            for item in pedido.itens:
                self._estoque.reservar(item.sku, item.quantidade)
                reservados.append((item.sku, item.quantidade))
        except ErroDeDominio:
            for sku, quantidade in reservados:
                self._estoque.liberar(sku, quantidade)
            raise  # o pedido não foi salvo, continua em rascunho

        self._repo.salvar(pedido)
        return pedido


class CancelarPedido:
    def __init__(self, repo: RepositorioPedidos, estoque: Estoque) -> None:
        self._repo = repo
        self._estoque = estoque

    def executar(self, pedido_id: str) -> Pedido:
        pedido = self._repo.obter(pedido_id)
        tinha_reserva = pedido.status is StatusPedido.CONFIRMADO
        pedido.cancelar()
        if tinha_reserva:
            for item in pedido.itens:
                self._estoque.liberar(item.sku, item.quantidade)
        self._repo.salvar(pedido)
        return pedido
