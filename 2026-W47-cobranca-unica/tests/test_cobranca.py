import threading

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


def test_segunda_requisicao_entre_consulta_e_registro_nao_duplica():
    """Intercala de forma controlada: a segunda requisição começa quando a primeira
    já consultou a chave e ainda não registrou a cobrança. Sem exclusão mútua,
    a segunda termina nessa janela e as duas registram uma cobrança."""
    servico = ServicoDeCobranca()
    segunda_terminou = threading.Event()
    threads: list[threading.Thread] = []

    def segunda_requisicao():
        servico.cobrar("a", "pedido-1", 100)
        segunda_terminou.set()

    def intercalar():
        servico.ao_consultar_chave = None
        t = threading.Thread(target=segunda_requisicao)
        threads.append(t)
        t.start()
        # Sem trava, a segunda termina aqui. Com trava, ela espera a primeira.
        segunda_terminou.wait(timeout=1)

    servico.ao_consultar_chave = intercalar
    servico.cobrar("a", "pedido-1", 100)
    threads[0].join(timeout=5)

    assert segunda_terminou.is_set()
    assert len(servico.cobrancas) == 1
