import random
import time
import os
import re

def preparar_clientes(vertices_req, arestas_req, arcos_req):
    clientes = []
    id_servico = 1
    for v, (demanda, custo_servico) in vertices_req:
        clientes.append({'tipo': 'n', 'id': id_servico, 'origem': v, 'destino': v, 'demanda': demanda, 'custo': custo_servico})
        id_servico += 1
    for (u, v), (custo_transporte, demanda, custo_servico) in arestas_req:
        clientes.append({'tipo': 'e', 'id': id_servico, 'origem': u, 'destino': v, 'demanda': demanda, 'custo': custo_servico})
        id_servico += 1
    for (u, v), (custo_transporte, demanda, custo_servico) in arcos_req:
        clientes.append({'tipo': 'a', 'id': id_servico, 'origem': u, 'destino': v, 'demanda': demanda, 'custo': custo_servico})
        id_servico += 1
    return clientes

def inicializar_rotas(clientes, deposito, distancias):
    rotas = []
    for cliente in clientes:
        rota = {
            'clientes': [cliente],
            'demanda_total': cliente['demanda'],
            'servicos': {(cliente['tipo'], cliente['id'])},
            'sequencia': [deposito, cliente['origem'], cliente['destino'], deposito]
        }
        rotas.append(rota)
    return rotas

def calcular_savings(rotas, distancias, deposito):
    savings = []
    for i in range(len(rotas)):
        for j in range(len(rotas)):
            if i == j:
                continue
            fim_i = rotas[i]['sequencia'][-2]
            ini_j = rotas[j]['sequencia'][1]
            saving = distancias[fim_i][deposito] + distancias[deposito][ini_j] - distancias[fim_i][ini_j]
            savings.append((saving, i, j))
    savings.sort(key=lambda x: (int(re.findall(r'\d+', str(x[1]))[0]), int(re.findall(r'\d+', str(x[2]))[0])))
    return savings

def juntar_rotas_iterativamente(rotas, distancias, deposito, capacidade):
    while True:
        savings = calcular_savings(rotas, distancias, deposito)
        melhor_gain = float('-inf')
        melhor_nova_rota = None
        melhor_i = melhor_j = -1

        for saving, i, j in savings:
            if i == j:
                continue

            rota_i = rotas[i]
            rota_j = rotas[j]

            if rota_i['servicos'] & rota_j['servicos']:
                continue

            nova_demanda = rota_i['demanda_total'] + rota_j['demanda_total']
            if nova_demanda > capacidade:
                continue

            opcoes_seq = [
                rota_i['sequencia'][:-1] + rota_j['sequencia'][1:],
                rota_i['sequencia'][:-1] + rota_j['sequencia'][-2:0:-1] + [deposito],
                [deposito] + rota_i['sequencia'][1:-1][::-1] + rota_j['sequencia'][1:],
                [deposito] + rota_i['sequencia'][1:-1][::-1] + rota_j['sequencia'][-2:0:-1] + [deposito],
            ]

            for seq in opcoes_seq:
                if seq[0] != deposito or seq[-1] != deposito:
                    continue

                servicos_visita = set()
                for k in range(len(seq) - 1):
                    u, v = seq[k], seq[k + 1]
                    for c in rota_i['clientes'] + rota_j['clientes']:
                        if (c['tipo'], c['id']) in servicos_visita:
                            continue
                        if (c['origem'] == u and c['destino'] == v) or \
                           (c['tipo'] == 'e' and (min(u,v), max(u,v)) == (min(c['origem'], c['destino']), max(c['origem'], c['destino']))):
                            servicos_visita.add((c['tipo'], c['id']))

                if len(servicos_visita) < len(rota_i['servicos'] | rota_j['servicos']):
                    continue

                custo = sum(distancias[seq[k]][seq[k+1]] for k in range(len(seq)-1))
                custo_serv = sum(c['custo'] for c in rota_i['clientes'] + rota_j['clientes'])
                gain = saving - (custo + custo_serv)
                if gain >= melhor_gain:
                    melhor_gain = gain
                    melhor_nova_rota = {
                        'clientes': rota_i['clientes'] + rota_j['clientes'],
                        'demanda_total': nova_demanda,
                        'servicos': rota_i['servicos'] | rota_j['servicos'],
                        'sequencia': seq
                    }
                    melhor_i, melhor_j = i, j

        if melhor_nova_rota is None:
            break

        novas_rotas = []
        for k in range(len(rotas)):
            if k != melhor_i and k != melhor_j:
                novas_rotas.append(rotas[k])
        novas_rotas.append(melhor_nova_rota)
        rotas = novas_rotas

    return rotas

def salvar_solucao(rotas, nome_arquivo, deposito, matriz_dist):
    with open(nome_arquivo, "w", encoding="utf-8") as f:
        custo_total_global = 0
        for rota in rotas:
            seq = rota["sequencia"]
            custo_transporte = sum(matriz_dist[seq[k]][seq[k + 1]] for k in range(len(seq) - 1))
            custo_servico = sum(c['custo'] for c in rota["clientes"])
            custo_total_global += custo_transporte + custo_servico

        f.write(f"{custo_total_global}\n")
        f.write(f"{len(rotas)}\n")
        f.write(f"{random.randint(10000000, 999999999)}\n")
        f.write(f"{int(time.time())}\n")

        for i, rota in enumerate(rotas, start=1):
            seq = rota["sequencia"]
            visitas = []
            custo_transporte = 0
            custo_servico = 0
            visitados = set()

            for k in range(len(seq) - 1):
                u = seq[k]
                v = seq[k + 1]
                custo_transporte += matriz_dist[u][v]
                for cliente in rota["clientes"]:
                    chave = (cliente["tipo"], cliente["id"])
                    if chave in visitados:
                        continue
                    if (cliente["origem"] == u and cliente["destino"] == v) or \
                       (cliente["tipo"] == 'e' and ((cliente["origem"], cliente["destino"]) == (min(u,v), max(u,v)))):
                        visitas.append(f"(S {cliente['id']},{u},{v})")
                        visitados.add(chave)
                        custo_servico += cliente['custo']

            total_visitas = len(visitas) + 2
            demanda_total = rota['demanda_total']
            linha = f" 0 1 {i} {demanda_total} {int(custo_transporte + custo_servico)}  {total_visitas} (D 0,1,1) "
            linha += " ".join(visitas) + " (D 0,1,1)\n"
            f.write(linha)
