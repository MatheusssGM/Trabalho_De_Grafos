import os
import re
import time
from algoritmo_construtivo import (
    preparar_clientes,
    salvar_solucao,
    grasp_rotas  
)
from leitor_grafo import (
    leitor_arquivo,
    criar_matriz_distancias
)

def extrair_numero(nome):
    numeros = re.findall(r'\d+', nome)
    return int(numeros[0]) if numeros else float('inf')

def main():
    pasta_dados = "dados"
    pasta_saida = os.path.join("solucoes")
    log_path = os.path.join("log_execucao.txt")

    if not os.path.isdir(pasta_dados):
        print("Erro: A pasta 'dados/' não foi encontrada.")
        return

    os.makedirs(pasta_saida, exist_ok=True)

    arquivos_dat = sorted([f for f in os.listdir(pasta_dados) if f.endswith('.dat')], key=extrair_numero)
    
    if not arquivos_dat:
        print("Nenhum arquivo .dat encontrado na pasta 'dados/'.")
        return

    with open(log_path, "w", encoding="utf-8") as log:
        log.write("LOG DE EXECUÇÃO - GRASP com realocação e refusão\n")
        log.write("====================================\n\n")

        for nome_arquivo in arquivos_dat:
            caminho_completo = os.path.join(pasta_dados, nome_arquivo)
            print(f"\n🔄 Processando: {nome_arquivo}")
            log.write(f"Instância: {nome_arquivo}\n")

            tempo_ini_total = time.time()

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

            print("🚀 Iniciando GRASP com 10 iterações...")
            tempo_ini_grasp = time.time()
            rotas_otimizadas = grasp_rotas(
                clientes, deposito, distancias, capacidade,
                iteracoes=10, ganho_minimo=0.1
            )
            tempo_fim_grasp = time.time()

            nome_saida = os.path.join(pasta_saida, f"sol-{nome_arquivo}")
            salvar_solucao(rotas_otimizadas, nome_saida, deposito, distancias)
            tempo_total = time.time() - tempo_ini_total

            # Log
            custo_total = sum(
                sum(distancias[r["sequencia"][k]][r["sequencia"][k+1]] for k in range(len(r["sequencia"]) - 1)) +
                sum(c["custo"] for c in r["clientes"])
                for r in rotas_otimizadas
            )

            print(f"✅ GRASP finalizado. Rotas: {len(rotas_otimizadas)}, Custo: {int(custo_total)}")
            print(f"💾 Solução salva em: {nome_saida}\n")

            log.write(f"  ➤ Rotas finais: {len(rotas_otimizadas)}\n")
            log.write(f"  ➤ Custo total final: {int(custo_total)}\n")
            log.write(f"  ➤ Tempo GRASP: {tempo_fim_grasp - tempo_ini_grasp:.2f} s\n")
            log.write(f"  ➤ Tempo total: {tempo_total:.2f} s\n")
            log.write("--------------------------------------------------\n")

    print(f"\n📄 Log de execução salvo em: {log_path}")

if __name__ == "__main__":
    main()
