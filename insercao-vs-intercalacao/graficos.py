"""Desenho dos gráficos (chamado pelo medir.py).

Cada gráfico é salvo em duas versões, uma para o tema claro e outra para o
tema escuro do GitHub. O README usa <picture> para mostrar a versão certa.
"""

import logging
import math
import os

import matplotlib
matplotlib.use("Agg")  # gera os PNGs sem precisar de janela
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter, NullFormatter

logging.getLogger("matplotlib.font_manager").setLevel(logging.ERROR)

PASTA = "figuras"

ROTULOS = {"insercao": "Inserção", "intercalacao": "Intercalação", "sorted": "sorted()"}
MARCADORES = {"insercao": "o", "intercalacao": "s", "sorted": "^"}

# Paleta categórica validada (daltonismo e contraste) para cada fundo.
TEMAS = {
    "claro": {
        "fundo": "#ffffff",
        "texto": "#1f2328",
        "texto2": "#59636e",
        "grade": "#d1d9e0",
        "eixo": "#9aa4af",
        "faixa": "#fbefe9",
        "serie": {"insercao": "#eb6834", "intercalacao": "#2a78d6", "sorted": "#1baf7a"},
        "teoria": "#59636e",
    },
    "escuro": {
        "fundo": "#0d1117",
        "texto": "#f0f6fc",
        "texto2": "#9198a1",
        "grade": "#262c36",
        "eixo": "#3d444d",
        "faixa": "#1c1714",
        "serie": {"insercao": "#d95926", "intercalacao": "#3987e5", "sorted": "#199e70"},
        "teoria": "#9198a1",
    },
}

FONTES = ["Inter", "Segoe UI", "Helvetica Neue", "Arial", "DejaVu Sans"]


def _br(v, casas=0):
    """Formata número no padrão brasileiro: 12 345,6"""
    s = f"{v:,.{casas}f}"
    return s.replace(",", " ").replace(".", ",")


def _estilo(t):
    plt.rcParams.update({
        "font.family": "sans-serif",
        "font.sans-serif": FONTES,
        "font.size": 11,
        "axes.facecolor": t["fundo"],
        "figure.facecolor": t["fundo"],
        "savefig.facecolor": t["fundo"],
        "axes.edgecolor": t["eixo"],
        "axes.labelcolor": t["texto2"],
        "axes.linewidth": 0.8,
        "xtick.color": t["texto2"],
        "ytick.color": t["texto2"],
        "xtick.major.size": 0,
        "ytick.major.size": 0,
        "xtick.minor.size": 0,
        "ytick.minor.size": 0,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.spines.left": False,
        "axes.grid": True,
        "grid.color": t["grade"],
        "grid.linewidth": 0.7,
        "legend.frameon": False,
        "legend.labelcolor": t["texto"],
    })


def _titulo(fig, t, titulo, subtitulo):
    fig.text(0.035, 0.955, titulo, ha="left", va="top", fontsize=16,
             fontweight="bold", color=t["texto"])
    fig.text(0.035, 0.885, subtitulo, ha="left", va="top", fontsize=11, color=t["texto2"])


def _eixo_log_n(ax, tamanhos):
    ax.set_xscale("log")
    ax.set_xticks(tamanhos)
    ax.xaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{int(v)}"))
    ax.xaxis.set_minor_formatter(NullFormatter())
    ax.grid(True, which="major", axis="both")
    ax.grid(False, which="minor")
    ax.set_xlabel("n (tamanho da lista)", labelpad=8)


def _rotulo_final(ax, t, x, y, texto, cor):
    """Rótulo direto no fim da linha: o nome em cor de texto, com um traço da cor da série."""
    ax.annotate(texto, xy=(x, y), xytext=(10, 0), textcoords="offset points",
                va="center", ha="left", fontsize=10.5, fontweight="bold", color=t["texto"],
                bbox=dict(boxstyle="round,pad=0.3", fc=t["fundo"], ec=cor, lw=1.4))


def _marca_virada(ax, t, n, texto, y_frac=0.93, lado="centro"):
    ax.axvline(n, color=t["texto2"], lw=1.1, ls=(0, (4, 3)), zorder=1)
    dx, ha = {"centro": (0, "center"), "direita": (8, "left")}[lado]
    ax.annotate(texto, xy=(n, y_frac), xycoords=("data", "axes fraction"),
                xytext=(dx, 0), textcoords="offset points", ha=ha, va="center",
                fontsize=10, color=t["texto"], fontweight="bold",
                bbox=dict(boxstyle="round,pad=0.4", fc=t["fundo"], ec=t["texto2"], lw=0.9))


def _linha(ax, t, xs, ys, nome, _nolegend=False):
    ax.plot(xs, ys, color=t["serie"][nome], lw=2.2, marker=MARCADORES[nome], ms=7,
            mec=t["fundo"], mew=1.6, zorder=3,
            label="_" + nome if _nolegend else ROTULOS[nome])


def _salvar(fig, nome, tema):
    os.makedirs(PASTA, exist_ok=True)
    fig.savefig(os.path.join(PASTA, f"{nome}-{tema}.png"), dpi=200)
    plt.close(fig)


# ---------------------------------------------------------------------------

def grafico_tempos(resumo, tamanhos, algoritmos, n_virada, repeticoes):
    for tema, t in TEMAS.items():
        _estilo(t)
        fig, ax = plt.subplots(figsize=(10, 5.8))
        fig.subplots_adjust(left=0.09, right=0.84, top=0.80, bottom=0.12)
        for nome in algoritmos:
            ys = [resumo[(n, nome)][0] for n in tamanhos]
            _linha(ax, t, tamanhos, ys, nome)
            _rotulo_final(ax, t, tamanhos[-1], ys[-1], ROTULOS[nome], t["serie"][nome])
        _eixo_log_n(ax, tamanhos)
        ax.set_yscale("log")
        ax.yaxis.set_major_formatter(FuncFormatter(
            lambda v, _: _br(v, 1) if v < 1 else _br(v)))
        ax.yaxis.set_minor_formatter(NullFormatter())
        ax.set_ylabel("tempo médio por ordenação (µs)", labelpad=8)
        ax.axvspan(tamanhos[0] * 0.9, n_virada, color=t["faixa"], zorder=0, lw=0)
        ax.text(tamanhos[0] * 1.15, 0.84, "◀  aqui a inserção é mais rápida",
                transform=ax.get_xaxis_transform(), ha="left", va="center", fontsize=10,
                color=t["serie"]["insercao"], fontweight="bold")
        _marca_virada(ax, t, n_virada, f"virada ≈ {n_virada}")
        ax.set_xlim(tamanhos[0] * 0.9, tamanhos[-1] * 1.12)
        _titulo(fig, t, "Tempo de ordenação",
                f"Média de {repeticoes} listas aleatórias por tamanho · escalas logarítmicas")
        _salvar(fig, "tempos", tema)


def grafico_comparacoes(resumo, tamanhos, algoritmos, repeticoes):
    ns = [tamanhos[0] * (tamanhos[-1] / tamanhos[0]) ** (i / 200) for i in range(201)]
    for tema, t in TEMAS.items():
        _estilo(t)
        fig, ax = plt.subplots(figsize=(10, 5.8))
        fig.subplots_adjust(left=0.09, right=0.84, top=0.80, bottom=0.12)
        ax.plot(ns, [n * math.log2(n) for n in ns], color=t["teoria"], lw=1.3,
                ls=(0, (5, 3)), zorder=2, label="n·log₂ n")
        ax.plot(ns, [math.lgamma(n + 1) / math.log(2) for n in ns], color=t["teoria"],
                lw=1.3, ls=(0, (1, 2)), zorder=2, label="log₂(n!)  ·  mínimo teórico")
        ax.plot(ns, [n * n / 4 for n in ns], color=t["serie"]["insercao"], lw=1.1,
                ls=(0, (1, 2)), alpha=0.7, zorder=2, label="n²/4")
        for nome in algoritmos:
            ys = [resumo[(n, nome)][2] for n in tamanhos]
            _linha(ax, t, tamanhos, ys, nome, _nolegend=True)
        fim = {nome: resumo[(tamanhos[-1], nome)][2] for nome in algoritmos}
        _rotulo_final(ax, t, tamanhos[-1], fim["insercao"], ROTULOS["insercao"],
                      t["serie"]["insercao"])
        # intercalação e sorted() quase se sobrepõem: separa os rótulos
        ax.annotate(ROTULOS["intercalacao"], xy=(tamanhos[-1], fim["intercalacao"]),
                    xytext=(10, 14), textcoords="offset points", va="center", fontsize=10.5,
                    fontweight="bold", color=t["texto"],
                    bbox=dict(boxstyle="round,pad=0.3", fc=t["fundo"],
                              ec=t["serie"]["intercalacao"], lw=1.4))
        ax.annotate(ROTULOS["sorted"], xy=(tamanhos[-1], fim["sorted"]),
                    xytext=(10, -14), textcoords="offset points", va="center", fontsize=10.5,
                    fontweight="bold", color=t["texto"],
                    bbox=dict(boxstyle="round,pad=0.3", fc=t["fundo"],
                              ec=t["serie"]["sorted"], lw=1.4))
        _eixo_log_n(ax, tamanhos)
        ax.set_yscale("log")
        ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _: _br(v)))
        ax.yaxis.set_minor_formatter(NullFormatter())
        ax.set_ylabel("comparações", labelpad=8)
        ax.set_xlim(tamanhos[0] * 0.9, tamanhos[-1] * 1.12)
        leg = ax.legend(loc="upper left", fontsize=10, handlelength=3, title="curvas teóricas",
                        title_fontsize=10)
        leg._legend_box.align = "left"
        leg.get_title().set_color(t["texto"])
        for txt in leg.get_texts():
            txt.set_color(t["texto2"])
        _titulo(fig, t, "Número de comparações",
                f"Média de {repeticoes} listas aleatórias por tamanho · com as curvas teóricas")
        _salvar(fig, "comparacoes", tema)


def grafico_virada(resumo, tamanhos, n_virada_tempo, n_virada_comp, repeticoes):
    for tema, t in TEMAS.items():
        _estilo(t)
        fig, (a1, a2) = plt.subplots(1, 2, figsize=(11, 5.2))
        fig.subplots_adjust(left=0.07, right=0.98, top=0.76, bottom=0.13, wspace=0.18)
        paineis = ((a1, 0, "Tempo (µs)", n_virada_tempo),
                   (a2, 2, "Comparações", n_virada_comp))
        for ax, idx, nome_eixo, nv in paineis:
            for nome in ("insercao", "intercalacao"):
                ax.plot(tamanhos, [resumo[(n, nome)][idx] for n in tamanhos],
                        color=t["serie"][nome], lw=2.2, label=ROTULOS[nome], zorder=3)
            ax.axvspan(tamanhos[0], nv, color=t["faixa"], zorder=0, lw=0)
            _marca_virada(ax, t, nv, f"virada: n ≈ {nv}", y_frac=0.55, lado="direita")
            ax.set_xlim(tamanhos[0], tamanhos[-1])
            ax.set_ylim(bottom=0)
            ax.set_xlabel("n", labelpad=6)
            ax.set_title(nome_eixo, loc="left", fontsize=12, fontweight="bold",
                         color=t["texto"], pad=10)
            ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _: _br(v)))
            leg = ax.legend(loc="upper left", fontsize=10)
        _titulo(fig, t, "Onde a intercalação passa à frente",
                f"Varredura de n = {tamanhos[0]} a {tamanhos[-1]} · {repeticoes} listas por "
                "tamanho · área sombreada: inserção vence")
        _salvar(fig, "virada", tema)
