# Cobrança única

Exemplo hipotético para estudo.

## O problema

O cliente envia uma cobrança. O serviço cobra, mas a resposta se perde no caminho (timeout, queda de rede). O cliente não sabe se a cobrança aconteceu e repete a requisição. Sem proteção, o mesmo pedido é cobrado duas vezes.

## O risco

Cobrança duplicada depois de uma repetição. Revisão e testes do caminho feliz não mostram esse risco, porque nele a resposta sempre chega.

## O teste que torna o risco visível

`test_repetir_apos_falha_gera_uma_unica_cobranca` simula a perda da resposta depois da cobrança, deixa o cliente repetir a mesma requisição e verifica que existe uma única cobrança.

O histórico de commits conta a história em passos pequenos:

1. o serviço entra sem proteção contra repetição;
2. o teste entra e falha (duas cobranças);
3. a correção entra e o mesmo teste passa;
4. os casos de chave reutilizada com outro valor e de uma segunda requisição que chega no meio da primeira completam a proteção.

## A correção

Cada requisição leva uma chave de idempotência. O serviço guarda a cobrança por chave: se a mesma chave chega de novo, devolve a cobrança já feita em vez de criar outra. A mesma chave com outro valor é recusada.

## Como rodar

```bash
pip install pytest
python -m pytest
```

## Que evidência isso gera

- Repetir a mesma requisição depois de uma resposta perdida não cria uma segunda cobrança.
- Uma segunda requisição com a mesma chave, disparada no exato intervalo entre a primeira consultar a chave e registrar a cobrança, não cria outra cobrança. O teste força esse intervalo de propósito e falha se a trava for removida.
- Reutilizar a chave com outro valor é recusado.

## O que isso não prova

- O teste cobre uma intercalação específica, em um único processo. Não é prova geral de ausência de condição de corrida.
- O armazenamento é em memória: não cobre vários processos, reinício do serviço nem expiração de chaves. Em produção, a chave precisa de armazenamento compartilhado com restrição de unicidade.
- Não cobre o cliente gerar uma chave nova a cada tentativa, que anula a proteção.
- Não substitui monitorar cobranças repetidas para a mesma operação.

## Fontes

- Google SRE Book, Postmortem Culture: https://sre.google/sre-book/postmortem-culture/
- Google SRE Book, Addressing Cascading Failures (repetições): https://sre.google/sre-book/addressing-cascading-failures/
- IETF, rascunho The Idempotency-Key HTTP Header Field: https://datatracker.ietf.org/doc/draft-ietf-httpapi-idempotency-key-header/
