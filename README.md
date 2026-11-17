# Mini projetos de Quality Engineering

Um laboratório pequeno por semana: um risco de qualidade, um teste que o torna visível e a correção que o teste passa a proteger.

Cada pasta `AAAA-Wnn-tema/` traz:

- `README.md`: o problema, o risco, como rodar, que evidência o teste gera, o que ele não prova e as fontes.
- `src/`: código curto em Python, só com a biblioteca padrão.
- `tests/`: testes com pytest.

Os cenários são exemplos hipotéticos, criados para estudo. Não representam sistemas reais.

## Como rodar uma semana

```bash
pip install pytest
cd 2026-W47-cobranca-unica
python -m pytest -q
```

## Semanas

| Semana | Tema | Pergunta |
|---|---|---|
| [2026-W47](2026-W47-cobranca-unica/) | Cobrança única | Repetir a requisição depois de uma falha cobra duas vezes? |

Licença: MIT.
