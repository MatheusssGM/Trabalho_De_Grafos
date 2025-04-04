import numpy as np

class Grafo:
    def __init__(self, n):
        self.n = n  # Número de vértices
        self.INF = float('inf')
        self.matriz = np.full((n, n), self.INF)
        np.fill_diagonal(self.matriz, 0)
        self.arestas = 0
        self.arcos = 0

    def adicionar_aresta(self, u, v, peso=1, bidirecional=True):
        self.matriz[u][v] = peso
        if bidirecional:
            self.matriz[v][u] = peso  # Grafo não direcionado
            self.arestas += 1  # Incrementa arestas para grafos não direcionados
        else:
            self.arcos += 1  # Incrementa arcos para grafos direcionados


def ler_grafo_input():
    n = int(input("Digite o número de vértices: "))  # Lê a quantidade de vértices
    grafo = Grafo(n)

    m = int(input("Digite o número de arestas/arcos: "))  # Lê a quantidade de arestas ou arcos

    print("Digite as arestas/arcos no formato: u v peso bidirecional (1 para sim, 0 para não)")
    for _ in range(m):
        u, v, peso, bidirecional = map(int, input().split())
        grafo.adicionar_aresta(u, v, peso, bidirecional == 1)

    return grafo


def qtd_vertices(grafo):
    return grafo.n


def qtd_arestas(grafo):
    return grafo.arestas


def qtd_arcos(grafo):
    return grafo.arcos


def densidade(grafo):
    if grafo.arcos > 0:  # Grafo direcionado
        return grafo.arcos / (grafo.n * (grafo.n - 1))
    else:  # Grafo não direcionado
        return (2 * grafo.arestas) / (grafo.n * (grafo.n - 1))


def componentes_conectados(grafo):
    visitado = [False] * grafo.n
    componentes = 0

    def dfs(v):
        visitado[v] = True
        for u in range(grafo.n):
            if grafo.matriz[v][u] != grafo.INF and not visitado[u]:
                dfs(u)

    for v in range(grafo.n):
        if not visitado[v]:
            componentes += 1
            dfs(v)
    
    return componentes


def grau_min_max(grafo):
    graus = [sum(1 for peso in grafo.matriz[i] if peso != grafo.INF and peso != 0) for i in range(grafo.n)]
    return min(graus), max(graus)


def floyd_warshall(grafo):
    n = grafo.n
    dist = grafo.matriz.copy()
    predecessor = np.full((n, n), -1)

    for i in range(n):
        for j in range(n):
            if dist[i][j] != grafo.INF and i != j:
                predecessor[i][j] = i  # Inicializando predecessores

    for k in range(n):
        for i in range(n):
            for j in range(n):
                if dist[i][k] + dist[k][j] < dist[i][j]:
                    dist[i][j] = dist[i][k] + dist[k][j]
                    predecessor[i][j] = predecessor[k][j]

    return dist, predecessor


def caminho_medio(dist):
    soma = np.sum(dist[dist != float('inf')])  # Somamos apenas distâncias finitas
    total_caminhos = np.count_nonzero(dist != float('inf')) - dist.shape[0]  # Ignora a diagonal principal
    return soma / total_caminhos


def diametro(dist):
    if np.any(dist == float('inf')):  # Verifica se há distâncias infinitas
        return float('inf')  # Retorna infinito se o grafo for desconectado
    return np.max(dist[dist != float('inf')])  # Caso contrário, retorna o maior valor finito

if __name__ == "__main__":
    # Ler o grafo do input
    grafo = ler_grafo_input()

    # Calcular estatísticas
    print("\n### Estatísticas do Grafo ###")
    print(f"Quantidade de vértices: {qtd_vertices(grafo)}")
    print(f"Quantidade de arestas: {qtd_arestas(grafo)}")
    print(f"Quantidade de arcos: {qtd_arcos(grafo)}")
    print(f"Densidade: {densidade(grafo):.4f}")
    print(f"Componentes conectados: {componentes_conectados(grafo)}")

    grau_min, grau_max = grau_min_max(grafo)
    print(f"Grau mínimo: {grau_min}")
    print(f"Grau máximo: {grau_max}")

    # Executar Floyd-Warshall
    dist, pred = floyd_warshall(grafo)

    print("\nMatriz de Caminhos Mais Curtos:")
    print(dist)

    print("\nMatriz de Predecessores:")
    print(pred)

    # Calcular caminho médio e diâmetro
    print(f"\nCaminho médio: {caminho_medio(dist):.4f}")
    print(f"Diâmetro do grafo: {diametro(dist)}")