import pytest

from pedidos.domain.dinheiro import Dinheiro
from pedidos.domain.excecoes import PedidoNaoEditavel, PedidoVazio, TransicaoInvalida
from pedidos.domain.pedido import Pedido, StatusPedido


def reais(valor):
    return Dinheiro.de_reais(valor)


def test_dinheiro():
    assert reais("10.50").centavos == 1050
    assert str(reais("1234.5")) == "R$ 1.234,50"
    assert reais(2).vezes(3) == reais(6)
    assert reais(1) + reais("0.5") == reais("1.5")
    with pytest.raises(ValueError):
        Dinheiro(-1)
    with pytest.raises(ValueError):
        reais("1.999")


def test_total_do_pedido():
    p = Pedido("1")
    p.adicionar_item("A", 2, reais("10"))
    p.adicionar_item("B", 1, reais("5.50"))
    assert p.total == reais("25.50")


def test_mesmo_sku_soma_quantidade():
    p = Pedido("1")
    p.adicionar_item("A", 2, reais("10"))
    p.adicionar_item("A", 3, reais("10"))
    assert len(p.itens) == 1
    assert p.itens[0].quantidade == 5


def test_mesmo_sku_com_preco_diferente_e_rejeitado():
    p = Pedido("1")
    p.adicionar_item("A", 1, reais("10"))
    with pytest.raises(ValueError):
        p.adicionar_item("A", 1, reais("11"))


@pytest.mark.parametrize("quantidade", [0, -1])
def test_quantidade_invalida(quantidade):
    with pytest.raises(ValueError):
        Pedido("1").adicionar_item("A", quantidade, reais("1"))


def test_remover_item():
    p = Pedido("1")
    p.adicionar_item("A", 1, reais("1"))
    p.remover_item("A")
    assert p.itens == ()
    with pytest.raises(KeyError):
        p.remover_item("A")


def test_confirmar_pedido_vazio_falha():
    with pytest.raises(PedidoVazio):
        Pedido("1").confirmar()


def test_ciclo_de_vida():
    p = Pedido("1")
    p.adicionar_item("A", 1, reais("1"))
    p.confirmar()
    assert p.status is StatusPedido.CONFIRMADO

    with pytest.raises(PedidoNaoEditavel):
        p.adicionar_item("B", 1, reais("1"))
    with pytest.raises(TransicaoInvalida):
        p.confirmar()

    p.cancelar()
    assert p.status is StatusPedido.CANCELADO
    with pytest.raises(TransicaoInvalida):
        p.cancelar()
