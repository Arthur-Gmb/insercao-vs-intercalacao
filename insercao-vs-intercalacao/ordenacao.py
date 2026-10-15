"""Ordenação por inserção e por intercalação (merge sort).

Cada método tem duas versões:
  - insercao / intercalacao: versão "limpa", usada para medir tempo;
  - insercao_contando / intercalacao_contando: mesma lógica, mas devolve
    também o número de comparações entre elementos.

As versões são separadas para que o custo de contar não entre na medição
de tempo. Nenhuma função altera a lista recebida: todas devolvem uma nova.
"""


def insercao(lista):
    """Ordenação por inserção. Devolve uma nova lista ordenada."""
    a = list(lista)
    for i in range(1, len(a)):
        chave = a[i]
        j = i - 1
        while j >= 0 and a[j] > chave:
            a[j + 1] = a[j]
            j -= 1
        a[j + 1] = chave
    return a


def intercalacao(lista):
    """Ordenação por intercalação (merge sort). Devolve uma nova lista ordenada."""
    if len(lista) <= 1:
        return list(lista)
    meio = len(lista) // 2
    esq = intercalacao(lista[:meio])
    dir = intercalacao(lista[meio:])
    return _intercalar(esq, dir)


def _intercalar(esq, dir):
    resultado = []
    i = j = 0
    while i < len(esq) and j < len(dir):
        if dir[j] < esq[i]:          # estável: em empate, fica o da esquerda
            resultado.append(dir[j])
            j += 1
        else:
            resultado.append(esq[i])
            i += 1
    resultado.extend(esq[i:])
    resultado.extend(dir[j:])
    return resultado


# ---------------------------------------------------------------------------
# Versões que contam comparações entre elementos
# ---------------------------------------------------------------------------

def insercao_contando(lista):
    """Igual a insercao, mas devolve (lista_ordenada, comparacoes)."""
    a = list(lista)
    comparacoes = 0
    for i in range(1, len(a)):
        chave = a[i]
        j = i - 1
        while j >= 0:
            comparacoes += 1
            if a[j] > chave:
                a[j + 1] = a[j]
                j -= 1
            else:
                break
        a[j + 1] = chave
    return a, comparacoes


def intercalacao_contando(lista):
    """Igual a intercalacao, mas devolve (lista_ordenada, comparacoes)."""
    if len(lista) <= 1:
        return list(lista), 0
    meio = len(lista) // 2
    esq, c1 = intercalacao_contando(lista[:meio])
    dir, c2 = intercalacao_contando(lista[meio:])
    resultado = []
    i = j = 0
    c = 0
    while i < len(esq) and j < len(dir):
        c += 1
        if dir[j] < esq[i]:
            resultado.append(dir[j])
            j += 1
        else:
            resultado.append(esq[i])
            i += 1
    resultado.extend(esq[i:])
    resultado.extend(dir[j:])
    return resultado, c1 + c2 + c
