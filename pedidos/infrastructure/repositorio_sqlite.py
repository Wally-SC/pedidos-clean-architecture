from __future__ import annotations

import sqlite3
from pathlib import Path

from pedidos.domain.dinheiro import Dinheiro
from pedidos.domain.excecoes import PedidoNaoEncontrado
from pedidos.domain.pedido import ItemPedido, Pedido, StatusPedido

_SCHEMA = """
CREATE TABLE IF NOT EXISTS pedidos (
    id     TEXT PRIMARY KEY,
    status TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS itens_pedido (
    pedido_id      TEXT    NOT NULL REFERENCES pedidos (id) ON DELETE CASCADE,
    sku            TEXT    NOT NULL,
    quantidade     INTEGER NOT NULL CHECK (quantidade > 0),
    preco_centavos INTEGER NOT NULL CHECK (preco_centavos >= 0),
    PRIMARY KEY (pedido_id, sku)
);
"""


class RepositorioPedidosSqlite:
    def __init__(self, caminho: str | Path = ":memory:") -> None:
        self._conexao = sqlite3.connect(str(caminho))
        self._conexao.execute("PRAGMA foreign_keys = ON")
        self._conexao.executescript(_SCHEMA)

    def fechar(self) -> None:
        self._conexao.close()

    def salvar(self, pedido: Pedido) -> None:
        with self._conexao:  # transação: ou grava tudo ou nada
            self._conexao.execute(
                "INSERT INTO pedidos (id, status) VALUES (?, ?) "
                "ON CONFLICT (id) DO UPDATE SET status = excluded.status",
                (pedido.id, pedido.status.value),
            )
            self._conexao.execute("DELETE FROM itens_pedido WHERE pedido_id = ?", (pedido.id,))
            self._conexao.executemany(
                "INSERT INTO itens_pedido (pedido_id, sku, quantidade, preco_centavos) VALUES (?, ?, ?, ?)",
                [(pedido.id, i.sku, i.quantidade, i.preco_unitario.centavos) for i in pedido.itens],
            )

    def obter(self, id_: str) -> Pedido:
        linha = self._conexao.execute("SELECT status FROM pedidos WHERE id = ?", (id_,)).fetchone()
        if linha is None:
            raise PedidoNaoEncontrado(id_)
        itens = [
            ItemPedido(sku, quantidade, Dinheiro(preco))
            for sku, quantidade, preco in self._conexao.execute(
                "SELECT sku, quantidade, preco_centavos FROM itens_pedido WHERE pedido_id = ? ORDER BY rowid",
                (id_,),
            )
        ]
        return Pedido(id_, itens, StatusPedido(linha[0]))
