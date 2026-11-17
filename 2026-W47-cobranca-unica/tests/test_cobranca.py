import pytest

from cobranca import ServicoDeCobranca, cobrar_com_repeticao


def test_chaves_diferentes_geram_cobrancas_diferentes():
    servico = ServicoDeCobranca()
    servico.cobrar("a", "pedido-1", 100)
    servico.cobrar("b", "pedido-2", 100)
    assert len(servico.cobrancas) == 2


def test_repetir_apos_falha_gera_uma_unica_cobranca():
    servico = ServicoDeCobranca(perder_proxima_resposta=True)
    cobranca = cobrar_com_repeticao(servico, "chave-1", "pedido-42", 9990)
    assert len(servico.cobrancas) == 1
    assert cobranca.pedido == "pedido-42"


def test_mesma_chave_com_outro_valor_e_recusada():
    servico = ServicoDeCobranca()
    servico.cobrar("a", "pedido-1", 100)
    with pytest.raises(ValueError):
        servico.cobrar("a", "pedido-1", 200)
