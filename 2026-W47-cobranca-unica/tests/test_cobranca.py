from cobranca import ServicoDeCobranca


def test_chaves_diferentes_geram_cobrancas_diferentes():
    servico = ServicoDeCobranca()
    servico.cobrar("a", "pedido-1", 100)
    servico.cobrar("b", "pedido-2", 100)
    assert len(servico.cobrancas) == 2
