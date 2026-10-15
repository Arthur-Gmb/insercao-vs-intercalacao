"""Testes dos dois métodos de ordenação.

Rodar:  python testes.py      (usa só a biblioteca padrão)
"""

import random
import unittest

from ordenacao import (
    insercao,
    intercalacao,
    insercao_contando,
    intercalacao_contando,
)

# Versões "só a lista" das funções que contam, para testá-las junto com as outras
METODOS = {
    "insercao": insercao,
    "intercalacao": intercalacao,
    "insercao_contando": lambda l: insercao_contando(l)[0],
    "intercalacao_contando": lambda l: intercalacao_contando(l)[0],
}


class Espiao:
    """Embrulha um valor e conta toda comparação < ou > feita com ele."""
    chamadas = 0

    def __init__(self, v, tag=None):
        self.v = v
        self.tag = tag

    def __lt__(self, outro):
        Espiao.chamadas += 1
        return self.v < outro.v

    def __gt__(self, outro):
        Espiao.chamadas += 1
        return self.v > outro.v


class TestaOrdenacao(unittest.TestCase):

    def confere(self, entrada):
        esperado = sorted(entrada)
        for nome, f in METODOS.items():
            with self.subTest(metodo=nome, entrada=entrada[:10]):
                copia = list(entrada)
                self.assertEqual(f(entrada), esperado)
                self.assertEqual(entrada, copia, "a lista original foi alterada")

    # --- casos difíceis exigidos ---------------------------------------
    def test_lista_vazia(self):
        self.confere([])

    def test_um_elemento(self):
        self.confere([42])

    def test_todos_iguais(self):
        self.confere([7] * 50)

    def test_ja_ordenada(self):
        self.confere(list(range(100)))

    def test_invertida(self):
        self.confere(list(range(100, 0, -1)))

    # --- casos adicionais ---------------------------------------------
    def test_dois_elementos(self):
        self.confere([2, 1])
        self.confere([1, 2])

    def test_negativos_e_repetidos(self):
        self.confere([3, -1, 3, 0, -1, 2, 2, -5, 3])

    def test_floats(self):
        self.confere([0.5, -2.25, 3.0, 0.5, 1e-9, -1e9])

    def test_strings(self):
        self.confere(["pera", "abacaxi", "uva", "Banana", "abacate"])

    def test_aleatorias(self):
        rng = random.Random(123)
        for n in list(range(0, 40)) + [100, 257, 1000]:
            self.confere([rng.randint(-50, 50) for _ in range(n)])

    def test_estabilidade(self):
        """Elementos iguais mantêm a ordem original (os dois são estáveis)."""
        rng = random.Random(7)
        dados = [Espiao(rng.randint(0, 5), tag=i) for i in range(200)]
        esperado = [(e.v, e.tag) for e in sorted(dados, key=lambda e: e.v)]
        for nome, f in METODOS.items():
            with self.subTest(metodo=nome):
                obtido = [(e.v, e.tag) for e in f(dados)]
                self.assertEqual(obtido, esperado)


class TestaContagem(unittest.TestCase):

    def test_contagem_bate_com_espiao(self):
        """O contador interno tem que bater com as comparações realmente feitas."""
        rng = random.Random(99)
        for n in [0, 1, 2, 3, 10, 50, 333]:
            dados = [Espiao(rng.randint(0, 100)) for _ in range(n)]
            for f in (insercao_contando, intercalacao_contando):
                with self.subTest(metodo=f.__name__, n=n):
                    Espiao.chamadas = 0
                    _, c = f(dados)
                    self.assertEqual(c, Espiao.chamadas)

    def test_insercao_melhor_e_pior_caso(self):
        for n in [1, 2, 10, 100]:
            _, c = insercao_contando(list(range(n)))
            self.assertEqual(c, max(n - 1, 0))             # já ordenada
            _, c = insercao_contando(list(range(n, 0, -1)))
            self.assertEqual(c, n * (n - 1) // 2)          # invertida

    def test_intercalacao_ja_ordenada(self):
        # Com a lista ordenada, cada intercalação gasta len(esquerda) comparações.
        # Para n = 2^k isso dá (n/2)·k.
        for k in range(0, 11):
            n = 2 ** k
            _, c = intercalacao_contando(list(range(n)))
            self.assertEqual(c, (n // 2) * k)

    def test_vazia_e_unitaria_nao_comparam(self):
        for f in (insercao_contando, intercalacao_contando):
            self.assertEqual(f([])[1], 0)
            self.assertEqual(f([5])[1], 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
