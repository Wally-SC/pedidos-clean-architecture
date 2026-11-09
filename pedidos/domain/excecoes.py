class ErroDeDominio(Exception):
    """Violação de uma regra de negócio."""


class PedidoNaoEncontrado(ErroDeDominio):
    def __init__(self, id_: str) -> None:
        super().__init__(f"pedido {id_} não encontrado")


class PedidoNaoEditavel(ErroDeDominio):
    """Só pedidos em rascunho podem ser alterados."""


class PedidoVazio(ErroDeDominio):
    def __init__(self) -> None:
        super().__init__("não é possível confirmar um pedido sem itens")


class TransicaoInvalida(ErroDeDominio):
    pass


class EstoqueInsuficiente(ErroDeDominio):
    def __init__(self, sku: str, solicitado: int, disponivel: int) -> None:
        super().__init__(f"estoque insuficiente para {sku}: pedido {solicitado}, disponível {disponivel}")
        self.sku = sku
