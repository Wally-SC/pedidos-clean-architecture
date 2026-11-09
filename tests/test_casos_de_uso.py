import itertools

import pytest

from pedidos.application.casos_de_uso import AdicionarItem, CancelarPedido, ConfirmarPedido, CriarPedido
from pedidos.domain.dinheiro import Dinheiro
from pedidos.domain.excecoes import EstoqueInsuficiente, PedidoNaoEncontrado
from pedidos.domain.pedido import StatusPedido
from pedidos.infrastructure.estoque_memoria import EstoqueEmMemoria
from pedidos.infrastructure.repositorio_memoria import RepositorioPedidosEmMemoria
from pedidos.infrastructure.repositorio_sqlite import RepositorioPedidosSqlite

PRECO = Dinheiro.de_reais("10")


@pytest.fixture(params=["memoria", "sqlite"])
def repo(request):
    """Os mesmos testes rodam contra as duas implementações do repositório."""
    if request.param == "memoria":
        yield RepositorioPedidosEmMemoria()
    else:
        r = RepositorioPedidosSqlite()
        yield r
        r.fechar()


@pytest.fixture
def estoque():
    return EstoqueEmMemoria({"A": 10, "B": 1})


def novo_pedido(repo, *itens):
    ids = itertools.count(1)
    pedido = CriarPedido(repo, gerar_id=lambda: f"p{next(ids)}").executar()
    for sku, qtd in itens:
        AdicionarItem(repo).executar(pedido.id, sku, qtd, PRECO)
    return pedido


def test_criar_e_recuperar(repo):
    pedido = novo_pedido(repo, ("A", 2))
    recuperado = repo.obter(pedido.id)
    assert recuperado.status is StatusPedido.RASCUNHO
    assert recuperado.total == Dinheiro.de_reais("20")


def test_pedido_inexistente(repo):
    with pytest.raises(PedidoNaoEncontrado):
        repo.obter("nao-existe")
    with pytest.raises(PedidoNaoEncontrado):
        AdicionarItem(repo).executar("nao-existe", "A", 1, PRECO)


def test_confirmar_reserva_estoque(repo, estoque):
    pedido = novo_pedido(repo, ("A", 4))
    ConfirmarPedido(repo, estoque).executar(pedido.id)
    assert repo.obter(pedido.id).status is StatusPedido.CONFIRMADO
    assert estoque.saldo("A") == 6


def test_falta_de_estoque_desfaz_reservas_parciais(repo, estoque):
    pedido = novo_pedido(repo, ("A", 3), ("B", 5))  # B só tem 1
    with pytest.raises(EstoqueInsuficiente):
        ConfirmarPedido(repo, estoque).executar(pedido.id)

    assert estoque.saldo("A") == 10  # reserva de A foi desfeita
    assert estoque.saldo("B") == 1
    assert repo.obter(pedido.id).status is StatusPedido.RASCUNHO  # nada foi persistido


def test_cancelar_confirmado_devolve_estoque(repo, estoque):
    pedido = novo_pedido(repo, ("A", 4))
    ConfirmarPedido(repo, estoque).executar(pedido.id)
    CancelarPedido(repo, estoque).executar(pedido.id)
    assert estoque.saldo("A") == 10
    assert repo.obter(pedido.id).status is StatusPedido.CANCELADO


def test_cancelar_rascunho_nao_mexe_no_estoque(repo, estoque):
    pedido = novo_pedido(repo, ("A", 4))
    CancelarPedido(repo, estoque).executar(pedido.id)
    assert estoque.saldo("A") == 10


def test_sqlite_persiste_em_arquivo(tmp_path):
    caminho = tmp_path / "pedidos.db"
    r1 = RepositorioPedidosSqlite(caminho)
    pedido = novo_pedido(r1, ("A", 2))
    r1.fechar()

    r2 = RepositorioPedidosSqlite(caminho)
    assert r2.obter(pedido.id).total == Dinheiro.de_reais("20")
    r2.fechar()
