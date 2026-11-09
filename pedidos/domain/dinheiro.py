from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, order=True)
class Dinheiro:
    """Value object imutável: valor em centavos de real."""

    centavos: int

    def __post_init__(self) -> None:
        if not isinstance(self.centavos, int) or isinstance(self.centavos, bool):
            raise TypeError("centavos deve ser int")
        if self.centavos < 0:
            raise ValueError("valor monetário não pode ser negativo")

    @classmethod
    def de_reais(cls, reais: str | int) -> "Dinheiro":
        from decimal import Decimal

        centavos = Decimal(str(reais)) * 100
        if centavos != centavos.to_integral_value():
            raise ValueError("use no máximo 2 casas decimais")
        return cls(int(centavos))

    @classmethod
    def zero(cls) -> "Dinheiro":
        return cls(0)

    def __add__(self, outro: "Dinheiro") -> "Dinheiro":
        return Dinheiro(self.centavos + outro.centavos)

    def vezes(self, quantidade: int) -> "Dinheiro":
        return Dinheiro(self.centavos * quantidade)

    def __str__(self) -> str:
        reais, resto = divmod(self.centavos, 100)
        return f"R$ {reais:,}".replace(",", ".") + f",{resto:02d}"
