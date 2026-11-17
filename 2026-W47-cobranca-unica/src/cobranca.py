"""Serviço de cobrança de brinquedo para o laboratório "Cobrança única".

O cliente envia uma cobrança com uma chave de idempotência. Se a resposta
se perde (timeout, queda de rede), o cliente repete a mesma requisição.
O serviço precisa registrar no máximo uma cobrança por chave.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from threading import Lock


class FalhaDeRede(Exception):
    """A cobrança pode ter sido feita, mas a resposta não chegou ao cliente."""


@dataclass(frozen=True)
class Cobranca:
    id: int
    pedido: str
    valor_centavos: int


@dataclass
class ServicoDeCobranca:
    cobrancas: list[Cobranca] = field(default_factory=list)
    _por_chave: dict[str, Cobranca] = field(default_factory=dict)
    _trava: Lock = field(default_factory=Lock)
    perder_proxima_resposta: bool = False

    def cobrar(self, chave: str, pedido: str, valor_centavos: int) -> Cobranca:
        if valor_centavos <= 0:
            raise ValueError("valor deve ser positivo")
        with self._trava:
            existente = self._por_chave.get(chave)
            if existente is not None:
                return existente
            nova = Cobranca(len(self.cobrancas) + 1, pedido, valor_centavos)
            self.cobrancas.append(nova)
            self._por_chave[chave] = nova
        if self.perder_proxima_resposta:
            self.perder_proxima_resposta = False
            raise FalhaDeRede("resposta perdida depois de cobrar")
        return nova


def cobrar_com_repeticao(servico: ServicoDeCobranca, chave: str, pedido: str,
                         valor_centavos: int, tentativas: int = 3) -> Cobranca:
    """Cliente que repete a mesma requisição (mesma chave) após falha de rede."""
    for tentativa in range(1, tentativas + 1):
        try:
            return servico.cobrar(chave, pedido, valor_centavos)
        except FalhaDeRede:
            if tentativa == tentativas:
                raise
    raise AssertionError("inalcançável")
