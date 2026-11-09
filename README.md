# pedidos-clean-architecture

Módulo de pedidos (carrinho, confirmação com reserva de estoque, cancelamento)
organizado em **Clean Architecture**, em Python puro e sem frameworks.
O objetivo é mostrar a separação de responsabilidades, não o volume de funcionalidades.

## Arquitetura

```
pedidos/
  domain/            # regras de negócio puras (sem I/O, sem bibliotecas externas)
    dinheiro.py      #   value object imutável (centavos)
    pedido.py        #   agregado Pedido + ItemPedido + status
    excecoes.py      #   erros de negócio
  application/       # casos de uso e contratos
    portas.py        #   Protocols: RepositorioPedidos, Estoque
    casos_de_uso.py  #   CriarPedido, AdicionarItem, ConfirmarPedido, CancelarPedido
  infrastructure/    # detalhes técnicos que implementam as portas
    repositorio_memoria.py
    repositorio_sqlite.py
    estoque_memoria.py
```

**Regra de dependência:** `infrastructure → application → domain`. O domínio não
conhece ninguém; a aplicação conhece só o domínio e as portas; a infraestrutura
implementa as portas. Por isso dá para trocar SQLite por outro banco, ou o estoque
por uma chamada HTTP, sem alterar uma linha de regra de negócio.

## Regras de negócio implementadas

- Só pedidos em **rascunho** podem ser alterados.
- Adicionar o mesmo SKU duas vezes soma as quantidades (preço precisa ser igual).
- Não se confirma pedido vazio.
- **Confirmar** reserva o estoque item a item; se um item falhar, as reservas já
  feitas são desfeitas e o pedido continua em rascunho (compensação, estilo saga simplificada).
- **Cancelar** um pedido confirmado devolve o estoque.

## Testes

```bash
pip install pytest
pytest
```

Os testes de casos de uso rodam contra **as duas implementações do repositório**
(fixture parametrizada), garantindo que ambas respeitam o mesmo contrato.

## Próximos passos possíveis

- Adaptador HTTP (FastAPI) chamando os casos de uso
- Eventos de domínio (`PedidoConfirmado`) e outbox
- Estoque como serviço externo com timeouts e retentativas
