import os
from algoritmo_construtivo import (
    preparar_clientes,
    inicializar_rotas,
    juntar_rotas_iterativamente,
    salvar_solucao,
)
from leitor_grafo import (
    leitor_arquivo,
    criar_matriz_distancias
)
import re
def extrair_numero(nome):  # adicione acima da função main
    numeros = re.findall(r'\d+', nome)
    return int(numeros[0]) if numeros else float('inf')




def main():
    pasta_dados = "dados"
    pasta_saida = os.path.join("solucoes")

    if not os.path.isdir(pasta_dados):
        print("Erro: A pasta 'dados/' não foi encontrada.")
        return

    os.makedirs(pasta_saida, exist_ok=True)

    arquivos_dat = sorted([f for f in os.listdir(pasta_dados) if f.endswith('.dat')], key=extrair_numero)
    
    if not arquivos_dat:
        print("Nenhum arquivo .dat encontrado na pasta 'dados/'.")
        return

    for nome_arquivo in arquivos_dat:
        caminho_completo = os.path.join(pasta_dados, nome_arquivo)
        print(f"🔄 Processando: {nome_arquivo}")

        dados = leitor_arquivo(caminho_completo)
        vertices = dados["vertices"]
        arestas = dados["arestas"]
        arcos = dados["arcos"]
        vertices_req = dados["vertices_requeridos"]
        arestas_req = dados["arestas_requeridas"]
        arcos_req = dados["arcos_requeridos"]
        capacidade = int(dados["header"].get("Capacity"))
        deposito = int(dados["header"].get("Depot Node"))

        distancias = criar_matriz_distancias(vertices, arestas, arcos)

        clientes = preparar_clientes(vertices_req, arestas_req, arcos_req)
        rotas_iniciais = inicializar_rotas(clientes, deposito, distancias)
        rotas_final = juntar_rotas_iterativamente(rotas_iniciais, distancias, deposito, capacidade)

        nome_saida = os.path.join(pasta_saida, f"sol-{nome_arquivo}")
        salvar_solucao(rotas_final, nome_saida, deposito, distancias)

        print(f"✅ Solução salva em: {nome_saida}\n")

if __name__ == "__main__":
    main()
