import numpy as np

def ler_arquivo(caminho_arquivo):
    with open(caminho_arquivo, "r", encoding="utf-8") as arquivo:
        linhas = arquivo.readlines()

    vertices = set()
    arestas = set()
    arcos = set()
    vertices_requeridos = set()
    arestas_requeridas = set()
    arcos_requeridos = set()
    secao_atual = None

    for linha in linhas:
        linha = linha.strip()

        # Identifica a seção atual com base no prefixo
        if linha.startswith("ReN."):
            secao_atual = "ReN"
            continue
        elif linha.startswith("ReE."):
            secao_atual = "ReE"
            continue
        elif linha.startswith("EDGE"):
            secao_atual = "EDGE"
            continue
        elif linha.startswith("ReA."):
            secao_atual = "ReA"
            continue
        elif linha.startswith("ARC"):
            secao_atual = "ARC"
            continue

        if linha and secao_atual:
            partes = linha.split("\t")
            try:
                if secao_atual == "ReN":
                    vertice = int(partes[0].replace("N", ""))
                    demanda = int(partes[1])
                    custo_servico = int(partes[2])
                    vertices_requeridos.add((vertice, (demanda, custo_servico)))
                    vertices.add(vertice)

                elif secao_atual in ["ReE", "EDGE"]:
                    origem, destino = int(partes[1]), int(partes[2])
                    vertices.update([origem, destino])
                    aresta = (min(origem, destino), max(origem, destino))
                    custo_transporte = int(partes[3])
                    arestas.add((aresta, custo_transporte))

                    if secao_atual == "ReE":
                        demanda = int(partes[4])
                        custo_servico = int(partes[5])
                        arestas_requeridas.add((aresta, (custo_transporte, demanda, custo_servico)))

                elif secao_atual in ["ReA", "ARC"]:
                    origem, destino = int(partes[1]), int(partes[2])
                    vertices.update([origem, destino])
                    arco = (origem, destino)
                    custo_transporte = int(partes[3])
                    arcos.add((arco, custo_transporte))

                    if secao_atual == "ReA":
                        demanda = int(partes[4])
                        custo_servico = int(partes[5])
                        arcos_requeridos.add((arco, (custo_transporte, demanda, custo_servico)))
            except ValueError:
                continue

    return vertices, arestas, arcos, vertices_requeridos, arestas_requeridas, arcos_requeridos

def calcular_graus(vertices, arestas, arcos):
    graus = {v: [0, 0, 0] for v in vertices}  # [grau, entrada, saída]

    for (u, v), _ in arestas:
        graus[u][0] += 1
        graus[v][0] += 1

    for (u, v), _ in arcos:
        graus[u][2] += 1  # saída
        graus[v][1] += 1  # entrada

    return tuple((v, tuple(g)) for v, g in graus.items())

def imprimir_graus(graus):
    grau_arestas_min = min(g[1][0] for g in graus)
    grau_arestas_max = max(g[1][0] for g in graus)
    print(f"Grau mínimo/máximo (arestas): {grau_arestas_min}/{grau_arestas_max}")

    grau_entrada_min = min(g[1][1] for g in graus)
    grau_entrada_max = max(g[1][1] for g in graus)
    print(f"Grau de entrada mínimo/máximo (arcos): {grau_entrada_min}/{grau_entrada_max}")

    grau_saida_min = min(g[1][2] for g in graus)
    grau_saida_max = max(g[1][2] for g in graus)
    print(f"Grau de saída mínimo/máximo (arcos): {grau_saida_min}/{grau_saida_max}")

    grau_total_min = min(sum(g[1]) for g in graus)
    grau_total_max = max(sum(g[1]) for g in graus)
    print(f"Grau total mínimo/máximo: {grau_total_min}/{grau_total_max}")

def calcular_densidade(num_vertices, num_arestas, num_arcos):
    max_arestas = (num_vertices * (num_vertices - 1)) / 2
    max_arcos = num_vertices * (num_vertices - 1)
    return (num_arestas + num_arcos) / (max_arestas + max_arcos)

def dijkstra(vertice_inicial, arestas, arcos):
    distancias = {vertice_inicial: 0}
    predecessores = {vertice_inicial: None}
    abertos = {vertice_inicial}

    while abertos:
        atual = min(abertos, key=lambda v: distancias.get(v, float('inf')))
        abertos.remove(atual)

        for (u, v), custo in arestas:
            if atual in [u, v]:
                vizinho = v if u == atual else u
                nova_dist = distancias[atual] + custo
                if vizinho not in distancias or nova_dist < distancias[vizinho]:
                    distancias[vizinho] = nova_dist
                    predecessores[vizinho] = atual
                    abertos.add(vizinho)

        for (u, v), custo in arcos:
            if u == atual:
                nova_dist = distancias[atual] + custo
                if v not in distancias or nova_dist < distancias[v]:
                    distancias[v] = nova_dist
                    predecessores[v] = atual
                    abertos.add(v)

    return distancias, predecessores

def montar_matriz_distancias(vertices, arestas, arcos):
    return {
        v: {u: dijkstra(v, arestas, arcos)[0].get(u, float('inf')) for u in vertices}
        for v in vertices
    }

def montar_matriz_predecessores(vertices, arestas, arcos):
    return {
        v: dijkstra(v, arestas, arcos)[1]
        for v in vertices
    }

def caminho_minimo(matriz_pred, origem, destino):
    caminho = []
    atual = destino
    while atual is not None:
        caminho.insert(0, atual)
        atual = matriz_pred[origem].get(atual)
    return caminho

def calcular_diametro(matriz_dist):
    return max(max(d.values()) for d in matriz_dist.values())

def calcular_caminho_medio(num_vertices, matriz_dist):
    soma = sum(sum(linha.values()) for linha in matriz_dist.values())
    return soma / (num_vertices * (num_vertices - 1))

def calcular_intermediacao(vertices, matriz_pred):
    intermediacao = {v: 0 for v in vertices}
    for origem in vertices:
        for destino in vertices:
            if origem != destino:
                caminho = caminho_minimo(matriz_pred, origem, destino)
                for v in caminho[1:-1]:
                    intermediacao[v] += 1
    return intermediacao

def exibir_metricas(vertices, arestas, arcos, vertices_req, arestas_req, arcos_req):
    densidade = calcular_densidade(len(vertices), len(arestas), len(arcos))
    matriz_dist = montar_matriz_distancias(vertices, arestas, arcos)
    matriz_pred = montar_matriz_predecessores(vertices, arestas, arcos)
    diametro = calcular_diametro(matriz_dist)
    caminho_medio = calcular_caminho_medio(len(vertices), matriz_dist)
    intermediacao = calcular_intermediacao(vertices, matriz_pred)
    graus = calcular_graus(vertices, arestas, arcos)

    print(f"Total de vértices: {len(vertices)}")
    print(f"Total de arestas: {len(arestas)}")
    print(f"Total de arcos: {len(arcos)}")
    print(f"Vértices requeridos: {len(vertices_req)}")
    print(f"Arestas requeridas: {len(arestas_req)}")
    print(f"Arcos requeridos: {len(arcos_req)}")
    print(f"Densidade do grafo: {densidade:.4f}")

    imprimir_graus(graus)

    print(f"Diâmetro do grafo: {diametro}")
    print(f"Caminho médio: {caminho_medio:.4f}")
    print("Intermediação por vértice:")
    for v, valor in intermediacao.items():
        print(f"  Vértice {v}: {valor}")

# Execução principal
caminho_arquivo = input("Informe o caminho do arquivo .dat para leitura do grafo: ")
vertices, arestas, arcos, vertices_req, arestas_req, arcos_req = ler_arquivo(caminho_arquivo)
exibir_metricas(vertices, arestas, arcos, vertices_req, arestas_req, arcos_req)
