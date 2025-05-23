import heapq
import random
import time
import math 
from copy import deepcopy

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

def calcular_savings_inicial(rotas, distancias, deposito):
    savings = []
    n = len(rotas)
    for i in range(n):
        for j in range(i+1, n):
            fim_i = rotas[i]['sequencia'][-2]
            ini_j = rotas[j]['sequencia'][1]
            saving = distancias[fim_i][deposito] + distancias[deposito][ini_j] - distancias[fim_i][ini_j]
            heapq.heappush(savings, (-saving, i, j))
    return savings

def juntar_rotas_com_heap(rotas, distancias, deposito, capacidade, ganho_minimo=0.1):
    savings = calcular_savings_inicial(rotas, distancias, deposito)
    rotas_ativas = {i for i in range(len(rotas))}
    mapa_rota = {i: rotas[i] for i in rotas_ativas}

    demanda_total = sum(r['demanda_total'] for r in rotas)
    minimo_rotas = math.ceil(demanda_total / capacidade)

    while savings and len(rotas_ativas) > minimo_rotas:
        neg_saving, i, j = heapq.heappop(savings)
        if i not in rotas_ativas or j not in rotas_ativas:
            continue

        rota_i = mapa_rota[i]
        rota_j = mapa_rota[j]

        if rota_i['demanda_total'] + rota_j['demanda_total'] > capacidade:
            continue
        if rota_i['servicos'] & rota_j['servicos']:
            continue

        seqs_candidatas = [
            rota_i['sequencia'][:-1] + rota_j['sequencia'][1:],              
            rota_i['sequencia'][:-1] + rota_j['sequencia'][-2:0:-1] + [deposito],
            [deposito] + rota_i['sequencia'][-2:0:-1] + rota_j['sequencia'][1:], 
            [deposito] + rota_i['sequencia'][-2:0:-1] + rota_j['sequencia'][-2:0:-1] + [deposito]
        ]

        melhor_seq = None
        melhor_ganho = float('-inf')

        custo_servico = sum(c['custo'] for c in rota_i['clientes'] + rota_j['clientes'])

        for seq in seqs_candidatas:
            if seq[0] != deposito or seq[-1] != deposito:
                continue

            custo_transporte = sum(distancias[seq[k]][seq[k+1]] for k in range(len(seq)-1))
            custo_total_novo = custo_transporte + custo_servico

            custo_transporte_antigo = sum(distancias[rota_i['sequencia'][k]][rota_i['sequencia'][k+1]] for k in range(len(rota_i['sequencia'])-1)) + \
                                     sum(distancias[rota_j['sequencia'][k]][rota_j['sequencia'][k+1]] for k in range(len(rota_j['sequencia'])-1))
            custo_total_antigo = custo_transporte_antigo + custo_servico

            ganho = custo_total_antigo - custo_total_novo

            if ganho > melhor_ganho and ganho >= ganho_minimo:
                melhor_ganho = ganho
                melhor_seq = seq

        if melhor_seq is None:
            continue

        nova_rota = {
            'clientes': rota_i['clientes'] + rota_j['clientes'],
            'demanda_total': rota_i['demanda_total'] + rota_j['demanda_total'],
            'servicos': rota_i['servicos'] | rota_j['servicos'],
            'sequencia': melhor_seq
        }
        nova_id = max(mapa_rota.keys()) + 1
        rotas_ativas.remove(i)
        rotas_ativas.remove(j)
        rotas_ativas.add(nova_id)
        mapa_rota[nova_id] = nova_rota

        for k in rotas_ativas:
            if k == nova_id:
                continue
            fim_nova = nova_rota['sequencia'][-2]
            ini_k = mapa_rota[k]['sequencia'][1]
            saving1 = distancias[fim_nova][deposito] + distancias[deposito][ini_k] - distancias[fim_nova][ini_k]

            fim_k = mapa_rota[k]['sequencia'][-2]
            ini_nova = nova_rota['sequencia'][1]
            saving2 = distancias[fim_k][deposito] + distancias[deposito][ini_nova] - distancias[fim_k][ini_nova]

            heapq.heappush(savings, (-saving1, nova_id, k))
            heapq.heappush(savings, (-saving2, k, nova_id))

    return [mapa_rota[i] for i in rotas_ativas]

def two_opt(seq, distancias, max_iter=1000, verbose=False):
    melhor_seq = seq
    melhor_custo = sum(distancias[seq[i]][seq[i+1]] for i in range(len(seq)-1))
    iter_count = 0
    melhorou = True

    while melhorou and iter_count < max_iter:
        melhorou = False
        iter_count += 1

        for i in range(1, len(seq) - 2):
            for j in range(i+1, len(seq) -1):
                if j - i == 1:
                    continue
                nova_seq = seq[:i] + seq[i:j][::-1] + seq[j:]
                novo_custo = sum(distancias[nova_seq[k]][nova_seq[k+1]] for k in range(len(nova_seq)-1))
                if novo_custo < melhor_custo:
                    melhor_seq = nova_seq
                    melhor_custo = novo_custo
                    melhorou = True
        seq = melhor_seq

        if verbose and iter_count % 100 == 0:
            print(f"2-opt iteração {iter_count}: custo atual {melhor_custo}")

    if verbose:
        print(f"2-opt finalizou após {iter_count} iterações com custo {melhor_custo}")

    return melhor_seq, melhor_custo

def aplicar_2opt_em_todas_rotas(rotas, distancias, max_iter=20, verbose=False):
    for idx, rota in enumerate(rotas, 1):
        if verbose:
            print(f"Iniciando 2-opt na rota {idx} com tamanho {len(rota['sequencia'])}")
        seq_atual = rota['sequencia']
        seq_melhor, _ = two_opt(seq_atual, distancias, max_iter=max_iter, verbose=verbose)
        rota['sequencia'] = seq_melhor
        if verbose:
            print(f"Rota {idx} otimizada")
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
                    if (cliente["tipo"] == 'a' and cliente["origem"] == u and cliente["destino"] == v) or \
                       (cliente["tipo"] == 'e' and ((min(u,v), max(u,v)) == (min(cliente["origem"], cliente["destino"]), max(cliente["origem"], cliente["destino"])))) or \
                       (cliente["tipo"] == 'n' and cliente["origem"] == u and cliente["destino"] == v):
                        visitas.append(f"(S {cliente['id']},{u},{v})")
                        visitados.add(chave)
                        custo_servico += cliente['custo']

            total_visitas = len(visitas) + 2
            demanda_total = rota['demanda_total']
            linha = f" 0 1 {i} {demanda_total} {int(custo_transporte + custo_servico)}  {total_visitas} (D 0,1,1) "
            linha += " ".join(visitas) + " (D 0,1,1)\n"
            f.write(linha)

def custo_total_rota(rota, distancias):
    seq = rota["sequencia"]
    custo_transporte = sum(distancias[seq[i]][seq[i+1]] for i in range(len(seq)-1))
    custo_servico = sum(c['custo'] for c in rota["clientes"])
    return custo_transporte + custo_servico

def realocar_rotas_pequenas(rotas, capacidade, distancias, deposito, verbose=False):
    novas_rotas = []
    pendentes = []

    for rota in rotas:
        if len(rota["clientes"]) <= 2:
            pendentes.append(rota)
        else:
            novas_rotas.append(rota)

    for rota_pequena in pendentes:
        clientes_nao_alocados = []

        for cliente in rota_pequena["clientes"]:
            alocado = False
            for rota in novas_rotas:
                if rota["demanda_total"] + cliente["demanda"] > capacidade:
                    continue
                if (cliente["tipo"], cliente["id"]) in rota["servicos"]:
                    continue

                nova_seq = rota["sequencia"][:-1] + [cliente["origem"], cliente["destino"], rota["sequencia"][-1]]
                nova_custo = sum(distancias[nova_seq[k]][nova_seq[k+1]] for k in range(len(nova_seq)-1))
                atual_custo = sum(distancias[rota["sequencia"][k]][rota["sequencia"][k+1]] for k in range(len(rota["sequencia"])-1))

                if nova_custo < atual_custo + 2 * distancias[rota["sequencia"][-2]][cliente["origem"]]:
                    rota["clientes"].append(cliente)
                    rota["demanda_total"] += cliente["demanda"]
                    rota["servicos"].add((cliente["tipo"], cliente["id"]))
                    rota["sequencia"] = nova_seq
                    alocado = True
                    break

            if not alocado:
                clientes_nao_alocados.append(cliente)

        if clientes_nao_alocados:
            if verbose:
                print(f"⚠️ Rota com {len(clientes_nao_alocados)} clientes não realocados foi mantida.")
            nova_rota = {
                'clientes': clientes_nao_alocados,
                'demanda_total': sum(c['demanda'] for c in clientes_nao_alocados),
                'servicos': {(c['tipo'], c['id']) for c in clientes_nao_alocados},
                'sequencia': [deposito] + [c['origem'] for c in clientes_nao_alocados] + [c['destino'] for c in reversed(clientes_nao_alocados)] + [deposito]
            }
            novas_rotas.append(nova_rota)
    return novas_rotas

def refundir_rotas(rotas, distancias, deposito, capacidade, ganho_minimo=0.1, verbose=False):
    novas_rotas = deepcopy(rotas)
    mudou = True

    while mudou:
        mudou = False
        n = len(novas_rotas)
        melhor_par = None
        melhor_seq = None
        melhor_ganho = 0

        for i in range(n):
            for j in range(i+1, n):
                r1, r2 = novas_rotas[i], novas_rotas[j]

                if r1["servicos"] & r2["servicos"]:
                    continue
                if r1["demanda_total"] + r2["demanda_total"] > capacidade:
                    continue
                seqs = [
                    r1['sequencia'][:-1] + r2['sequencia'][1:],
                    r1['sequencia'][:-1] + r2['sequencia'][-2:0:-1] + [deposito],
                    [deposito] + r1['sequencia'][-2:0:-1] + r2['sequencia'][1:],
                    [deposito] + r1['sequencia'][-2:0:-1] + r2['sequencia'][-2:0:-1] + [deposito],
                ]
                custo_servico = sum(c['custo'] for c in r1['clientes'] + r2['clientes'])
                custo_antigo = custo_total_rota(r1, distancias) + custo_total_rota(r2, distancias)

                for seq in seqs:
                    if seq[0] != deposito or seq[-1] != deposito:
                        continue

                    servicos_visita = set()
                    for c in r1['clientes'] + r2['clientes']:
                        servicos_visita.add((c['tipo'], c['id']))
                    if len(servicos_visita) != len(r1['clientes']) + len(r2['clientes']):
                        continue

                    custo_novo = sum(distancias[seq[k]][seq[k+1]] for k in range(len(seq)-1)) + custo_servico
                    ganho = custo_antigo - custo_novo
                    if ganho > melhor_ganho and ganho >= ganho_minimo:
                        melhor_ganho = ganho
                        melhor_par = (i, j)
                        melhor_seq = seq

        if melhor_par:
            i, j = melhor_par
            novos_clientes = novas_rotas[i]["clientes"] + novas_rotas[j]["clientes"]
            novos_servicos = novas_rotas[i]["servicos"] | novas_rotas[j]["servicos"]
            nova_rota = {
                "clientes": novos_clientes,
                "demanda_total": novas_rotas[i]["demanda_total"] + novas_rotas[j]["demanda_total"],
                "servicos": novos_servicos,
                "sequencia": melhor_seq
            }
            novas = [r for idx, r in enumerate(novas_rotas) if idx not in (i, j)]
            novas.append(nova_rota)
            novas_rotas = novas
            mudou = True
            if verbose:
                print(f"Refundiu rotas {i} e {j} -> total agora: {len(novas_rotas)}")
        else:
            if verbose:
                print("Nenhuma fusão adicional possível, encerrando refusão.")

    return novas_rotas

def grasp_rotas(clientes, deposito, distancias, capacidade, iteracoes=5, ganho_minimo=0.1):
    melhor_solucao = None
    melhor_custo = float('inf')

    for iter in range(iteracoes):
        print(f"  ➤ GRASP iteração {iter+1} de {iteracoes}")
        random.shuffle(clientes)
        rotas = inicializar_rotas(clientes, deposito, distancias)
        rotas = juntar_rotas_com_heap(rotas, distancias, deposito, capacidade, ganho_minimo)
        rotas = aplicar_2opt_em_todas_rotas(rotas, distancias, max_iter=20, verbose=False)
        rotas = realocar_rotas_pequenas(rotas, capacidade, distancias, deposito)
        rotas = refundir_rotas(rotas, distancias, deposito, capacidade, ganho_minimo)
        custo_atual = sum(custo_total_rota(r, distancias) for r in rotas)
        if custo_atual < melhor_custo:
            melhor_custo = custo_atual
            melhor_solucao = deepcopy(rotas)

    return melhor_solucao
