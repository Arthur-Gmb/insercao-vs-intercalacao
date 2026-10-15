"""Roda todas as medições e refaz, do zero:

  dados.csv                   números brutos (uma linha por tamanho × repetição × algoritmo)
  virada.csv                  números brutos da varredura fina (n = 2..120)
  figuras/tempos-*.png        tempo médio × n
  figuras/comparacoes-*.png   comparações médias × n (com sorted() e as curvas teóricas)
  figuras/virada-*.png        varredura fina, para localizar o ponto de virada

Cada figura sai em duas versões (claro e escuro), para o tema do GitHub.

Rodar:  python medir.py
"""

import csv
import gc
import math
import random
import statistics
import sys
import time

from ordenacao import insercao, intercalacao, insercao_contando, intercalacao_contando
import graficos

TAMANHOS = [5, 10, 20, 30, 50, 75, 100, 200, 500, 1000]
REPETICOES = 30          # o enunciado pede no mínimo 10
SEMENTE = 2026           # torna as listas reproduzíveis
TAMANHOS_VIRADA = list(range(2, 121))
REPETICOES_VIRADA = 30

ALGORITMOS = {
    "insercao": insercao,
    "intercalacao": intercalacao,
    "sorted": sorted,
}


# ---------------------------------------------------------------------------
# Contagem de comparações do sorted() (extra)
# ---------------------------------------------------------------------------

class Contavel:
    """Guarda um valor e conta quantas vezes __lt__ é chamado.

    O sorted() compara os elementos só com <, então o contador revela
    todas as comparações que ele fez.
    """
    __slots__ = ("v",)
    chamadas = 0

    def __init__(self, v):
        self.v = v

    def __lt__(self, outro):
        Contavel.chamadas += 1
        return self.v < outro.v


def comparacoes_sorted(lista):
    embrulhada = [Contavel(x) for x in lista]
    Contavel.chamadas = 0
    sorted(embrulhada)
    return Contavel.chamadas


CONTADORES = {
    "insercao": lambda l: insercao_contando(l)[1],
    "intercalacao": lambda l: intercalacao_contando(l)[1],
    "sorted": comparacoes_sorted,
}


# ---------------------------------------------------------------------------
# Medição
# ---------------------------------------------------------------------------

def execucoes_por_medida(n):
    """Listas pequenas ordenam em ~1 µs, perto da resolução do relógio.
    Por isso cada medida executa o algoritmo k vezes seguidas sobre a mesma
    lista e divide o tempo por k (k = 1 para listas grandes)."""
    return max(1, 1000 // n)


def cronometrar(f, lista, k):
    """Tempo médio (ns) de uma execução de f(lista), medido em k execuções."""
    gc.disable()
    t0 = time.perf_counter_ns()
    for _ in range(k):
        f(lista)
    t1 = time.perf_counter_ns()
    gc.enable()
    return (t1 - t0) / k


def medir(tamanhos, repeticoes, rng, rotulo):
    """Devolve as linhas brutas: (n, repeticao, algoritmo, tempo_ns, comparacoes, execucoes)."""
    linhas = []
    for i, n in enumerate(tamanhos, 1):
        k = execucoes_por_medida(n)
        for rep in range(1, repeticoes + 1):
            lista = [rng.randint(0, 10 * n) for _ in range(n)]
            ordem = list(ALGORITMOS)
            rng.shuffle(ordem)          # sorteia a ordem para não favorecer ninguém
            for nome in ordem:
                t = cronometrar(ALGORITMOS[nome], lista, k)
                c = CONTADORES[nome](lista)
                linhas.append((n, rep, nome, round(t, 1), c, k))
        _progresso(rotulo, i, len(tamanhos))
    return linhas


def resumir(linhas):
    """{(n, algoritmo): (tempo_medio_us, desvio_us, comparacoes_medias)}"""
    grupos = {}
    for n, _, nome, t, c, _k in linhas:
        grupos.setdefault((n, nome), ([], []))
        grupos[(n, nome)][0].append(t / 1000)
        grupos[(n, nome)][1].append(c)
    return {
        k: (statistics.mean(ts), statistics.stdev(ts) if len(ts) > 1 else 0.0,
            statistics.mean(cs))
        for k, (ts, cs) in grupos.items()
    }


def salvar_csv(caminho, linhas):
    with open(caminho, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["n", "repeticao", "algoritmo", "tempo_ns", "comparacoes", "execucoes"])
        w.writerows(linhas)


def primeiro_n_vencedor(tamanhos, resumo, indice):
    """Menor n a partir do qual a intercalação fica abaixo da inserção em todos os n seguintes."""
    resposta = None
    for n in reversed(tamanhos):
        if resumo[(n, "intercalacao")][indice] < resumo[(n, "insercao")][indice]:
            resposta = n
        else:
            break
    return resposta


# ---------------------------------------------------------------------------
# Saída no terminal
# ---------------------------------------------------------------------------

def _progresso(rotulo, i, total):
    largura = 28
    cheio = round(largura * i / total)
    print(f"\r  {rotulo:<22} [{'█' * cheio}{'·' * (largura - cheio)}] {i}/{total}",
          end="" if i < total else "\n", flush=True)


def tabela_md(resumo, indice):
    cab = "| n | Inserção | Intercalação | sorted() |\n|---:|---:|---:|---:|\n"
    corpo = "".join(
        f"| {n} | " + " | ".join(graficos._br(resumo[(n, a)][indice], 1) for a in ALGORITMOS)
        + " |\n"
        for n in TAMANHOS
    )
    return cab + corpo


def main():
    try:   # evita erro de acentos no terminal do Windows
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except AttributeError:
        pass

    rng = random.Random(SEMENTE)
    print("\nInserção × Intercalação — medições\n")

    linhas = medir(TAMANHOS, REPETICOES, rng, "tamanhos do enunciado")
    linhas_v = medir(TAMANHOS_VIRADA, REPETICOES_VIRADA, rng, "varredura fina")
    salvar_csv("dados.csv", linhas)
    salvar_csv("virada.csv", linhas_v)
    resumo = resumir(linhas)
    resumo_v = resumir(linhas_v)

    virada_tempo = primeiro_n_vencedor(TAMANHOS_VIRADA, resumo_v, 0)
    virada_comp = primeiro_n_vencedor(TAMANHOS_VIRADA, resumo_v, 2)

    print("  gráficos...", end="", flush=True)
    graficos.grafico_tempos(resumo, TAMANHOS, list(ALGORITMOS), virada_tempo, REPETICOES)
    graficos.grafico_comparacoes(resumo, TAMANHOS, list(ALGORITMOS), REPETICOES)
    graficos.grafico_virada(resumo_v, TAMANHOS_VIRADA, virada_tempo, virada_comp,
                            REPETICOES_VIRADA)
    print(" ok\n")

    print("Tempo médio (µs)\n")
    print(tabela_md(resumo, 0))
    print("Comparações médias\n")
    print(tabela_md(resumo, 2))

    print("Ponto de virada (intercalação passa a vencer e não perde mais):")
    print(f"  tempo,       tamanhos do enunciado: n = {primeiro_n_vencedor(TAMANHOS, resumo, 0)}")
    print(f"  comparações, tamanhos do enunciado: n = {primeiro_n_vencedor(TAMANHOS, resumo, 2)}")
    print(f"  tempo,       varredura fina:        n = {virada_tempo}")
    print(f"  comparações, varredura fina:        n = {virada_comp}")

    print("\nsorted() × limites teóricos (comparações):")
    for n in TAMANHOS:
        c = resumo[(n, "sorted")][2]
        lim = math.lgamma(n + 1) / math.log(2)
        nlogn = n * math.log2(n)
        print(f"  n={n:5d}  sorted={c:9.1f}  log2(n!)={lim:9.1f}  n·log2 n={nlogn:9.1f}"
              f"  sorted/n·log2 n={c / nlogn:.3f}  sorted/log2(n!)={c / lim:.3f}")

    print("\nArquivos gerados: dados.csv, virada.csv e figuras/*.png\n")


if __name__ == "__main__":
    main()
