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


class TravaObservada:
    """Trava que avisa quando outra thread (que não a primeira) tenta entrar nela."""

    def __init__(self, ao_tentar_entrar):
        self._trava = threading.Lock()
        self._ao_tentar_entrar = ao_tentar_entrar
        self._primeira = threading.current_thread()

    def __enter__(self):
        if threading.current_thread() is not self._primeira:
            self._ao_tentar_entrar()
        self._trava.acquire()
        return self

    def __exit__(self, *exc):
        self._trava.release()
        return False


def test_segunda_requisicao_entre_consulta_e_registro_nao_duplica():
    """Intercala de forma controlada: a segunda requisição começa quando a primeira
    já consultou a chave e ainda não registrou a cobrança. A primeira só continua
    depois de um destes fatos: a segunda chegou à trava (e vai esperar) ou a segunda
    já terminou (não havia exclusão mútua). No segundo caso, surgem duas cobranças."""
    servico = ServicoDeCobranca()
    segunda_chegou = threading.Event()
    servico._trava = TravaObservada(segunda_chegou.set)
    threads: list[threading.Thread] = []

    def segunda_requisicao():
        servico.cobrar("a", "pedido-1", 100)
        segunda_chegou.set()

    def intercalar():
        servico.ao_consultar_chave = None
        t = threading.Thread(target=segunda_requisicao)
        threads.append(t)
        t.start()
        # O prazo só protege contra travamento; a ordem vem do evento.
        assert segunda_chegou.wait(timeout=10), "a segunda requisição não avançou"

    servico.ao_consultar_chave = intercalar
    servico.cobrar("a", "pedido-1", 100)
    threads[0].join(timeout=10)

    assert not threads[0].is_alive()
    assert len(servico.cobrancas) == 1
