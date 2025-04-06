#*******************************************************************#

                #PROJETO DE ALGORITMOS EM GRAFOS#
            
   #Alunos: Arthur Soares Marques , Matheus Gomes Monteiro#

#*******************************************************************#


def leitor_arquivo(path):
    try:
        with open(path, "r", encoding="utf-8") as arquivo:
            linhas = arquivo.readlines()
    except FileNotFoundError:
        print(f"Erro: Arquivo '{path}' não encontrado.")
        exit()
    except Exception as e:
        print(f"Erro ao ler o arquivo: {e}")
        exit()

    vertices = set()
    arestas = set()
    arcos = set()
    vertices_requeridos = set()
    arestas_requeridas = set()
    arcos_requeridos = set()
    secao_atual = None

    for linha in linhas:
        linha = linha.strip()

        # Ignora linhas vazias ou comentários
        if not linha or linha.startswith("//") or linha.startswith("Name:"):
            continue

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
                print(f"Erro ao processar linha: {linha}")
                continue

    if not vertices:
        print("Erro: Nenhum vértice encontrado no arquivo.")
        exit()

    return vertices, arestas, arcos, vertices_requeridos, arestas_requeridas, arcos_requeridos


def validar_grafo(vertices, arestas, arcos):
    for (u, v), _ in arestas:
        if u not in vertices or v not in vertices:
            print(f"Erro: Aresta ({u}, {v}) contém vértices inexistentes.")
            exit()

    for (u, v), _ in arcos:
        if u not in vertices or v not in vertices:
            print(f"Erro: Arco ({u}, {v}) contém vértices inexistentes.")
            exit()

    print("Grafo validado com sucesso.")


def calcula_graus(vertices, arestas, arcos):
    grausT = {v: [0, 0, 0] for v in vertices}  # [grau, entrada, saída]

    for (u, v), _ in arestas:
        grausT[u][0] += 1
        grausT[v][0] += 1

    for (u, v), _ in arcos:
        grausT[u][2] += 1  # saída
        grausT[v][1] += 1  # entrada

    return tuple((v, tuple(g)) for v, g in grausT.items())


def imprimir_graus(graus):
    grau_min = min(sum(g[1]) for g in graus)
    grau_max = max(sum(g[1]) for g in graus)
    print(f"Grau mínimo: {grau_min}")
    print(f"Grau máximo: {grau_max}")


def calcular_densidade(num_vertices, num_arestas, num_arcos):
    arestasT = (num_vertices * (num_vertices - 1)) / 2
    arcosT = num_vertices * (num_vertices - 1)
    if num_vertices < 2:  # Densidade não definida para menos de 2 vértices
        return 0
    if arestasT == 0 or arcosT == 0:  # Densidade não definida para arestas ou arcos zero
        return 0
    if num_arestas > arestasT or num_arcos > arcosT:  # Limite de arestas e arcos
        print("Erro: O número de arestas ou arcos excede o máximo permitido.")
        exit()
    return (num_arestas + num_arcos) / (arestasT + arcosT)


def floyd_warshall(vertices, arestas, arcos):
    # Inicializa as matrizes de distâncias e predecessores
    distancias = {v: {u: float('inf') for u in vertices} for v in vertices}
    predecessores = {v: {u: None for u in vertices} for v in vertices}

    # Define a distância de um vértice para ele mesmo como 0
    for v in vertices:
        distancias[v][v] = 0

    # Adiciona as distâncias das arestas
    for (u, v), custo in arestas:
        distancias[u][v] = custo
        distancias[v][u] = custo
        predecessores[u][v] = u
        predecessores[v][u] = v

    # Adiciona as distâncias dos arcos
    for (u, v), custo in arcos:
        distancias[u][v] = custo
        predecessores[u][v] = u

    # Aplica o algoritmo de Floyd-Warshall

    for k in vertices:
        for i in vertices:
            for j in vertices:
                if distancias[i][j] > distancias[i][k] + distancias[k][j]:
                    distancias[i][j] = distancias[i][k] + distancias[k][j]
                    predecessores[i][j] = predecessores[k][j]

    return distancias, predecessores


def criar_matriz_distancias(vertices, arestas, arcos):
    distancias, _ = floyd_warshall(vertices, arestas, arcos)
    return distancias


def criar_matriz_predecessores(vertices, arestas, arcos):
    _, predecessores = floyd_warshall(vertices, arestas, arcos)
    return predecessores


def caminho_minimo(matriz_pred, origem, destino):
    caminho = []
    atual = destino
    while atual is not None:
        caminho.insert(0, atual)
        if atual == origem:  # Caminho completo
            break
        atual = matriz_pred[origem].get(atual)
    if caminho[0] != origem:  # Verifica se o caminho é válido
        return []  # Retorna um caminho vazio se não houver conexão
    return caminho


def calcular_diametro(matriz_dist):
    diametro = 0
    for d in matriz_dist.values():
        dist_max = max(v for v in d.values() if v < float('inf'))
        diametro = max(diametro, dist_max)
    return diametro


def calcular_caminho_medio(num_vertices, matriz_dist):
    soma = 0
    count = 0
    for linha in matriz_dist.values():
        for valor in linha.values():
            if valor < float('inf'):
                soma += valor

    return soma / (num_vertices * (num_vertices - 1))


def calcular_intermediacao(vertices, matriz_pred):
    intermediacao = {v: 0 for v in vertices}
    for origem in vertices:
        for destino in vertices:
            if origem != destino:
                caminho = caminho_minimo(matriz_pred, origem, destino)
                if len(caminho) > 1:  # Verifica se existe um caminho válido
                    for v in caminho[1:-1]:  # Exclui origem e destino
                        intermediacao[v] += 1
    return intermediacao


def exibirDados(vertices, arestas, arcos, vertices_req, arestas_req, arcos_req):
    try:
        validar_grafo(vertices, arestas, arcos)
        print("                             ")
        print("**** Dados do Grafo ****")
        print(f"Total de vértices: {len(vertices)}")
        print(f"Total de arestas: {len(arestas)}")
        print(f"Total de arcos: {len(arcos)}")
        print(f"Vértices requeridos: {len(vertices_req)}")
        print(f"Arestas requeridas: {len(arestas_req)}")
        print(f"Arcos requeridos: {len(arcos_req)}")

        densidade = calcular_densidade(len(vertices), len(arestas), len(arcos))
        print(f"Densidade do grafo: {densidade:.4f}")

        matriz_dist = criar_matriz_distancias(vertices, arestas, arcos)
        matriz_pred = criar_matriz_predecessores(vertices, arestas, arcos)

        diametro = calcular_diametro(matriz_dist)
        print(f"Diâmetro do grafo: {diametro}")

        caminho_medio = calcular_caminho_medio(len(vertices), matriz_dist)
        print(f"Caminho médio: {caminho_medio:.4f}")

        intermediacao = calcular_intermediacao(vertices, matriz_pred)
        graus = calcula_graus(vertices, arestas, arcos)

        imprimir_graus(graus)
        print("                             ")
        print("**** Intermediação por vértice ****")
        for v, valor in intermediacao.items():
            print(f"Vértice ({v}): {valor}")
    except Exception as e:
        print(f"Erro ao calcular métricas: {e}")
        exit()


# Main Frame
try:
    path = input("Informe o caminho do arquivo .dat para leitura do grafo: ")
    if not path.endswith(".dat"):
        raise ValueError("O arquivo deve ter a extensão .dat.")
    vertices, arestas, arcos, vertices_req, arestas_req, arcos_req = leitor_arquivo(path)
    exibirDados(vertices, arestas, arcos, vertices_req, arestas_req, arcos_req)
except Exception as e:
    print(f"Erro durante a execução: {e}")