
# 🔍 Análise de Grafos - Etapa 1  
**Autor:** Arthur Soares Marques  
**Curso:** Ciência da Computação - Universidade Federal de Lavras (UFLA)  

## 📌 Descrição

Este projeto é parte da Etapa 1 de um trabalho prático da disciplina de Teoria dos Grafos. O objetivo é realizar a leitura e análise de grafos a partir de arquivos `.dat`, calculando diversas métricas relevantes para a estrutura do grafo.

As funcionalidades implementadas até o momento incluem leitura do arquivo, verificação de integridade do grafo e cálculo de métricas estruturais utilizando algoritmos clássicos.

## 📁 Estrutura do Arquivo `.dat`

O arquivo de entrada deve conter as seguintes seções, podendo incluir:
- `ReN.` – Vértices requeridos
- `ReE.` – Arestas requeridas
- `EDGE` – Arestas gerais
- `ReA.` – Arcos requeridos
- `ARC` – Arcos gerais

Cada seção contém dados sobre os componentes do grafo, como vértices, arestas e arcos, juntamente com custos e demandas (quando aplicável).

## ⚙️ Funcionalidades Implementadas

- 📥 **Leitura do grafo** a partir de um arquivo `.dat`
- ✅ **Validação de integridade** do grafo (verifica se arestas e arcos se referem a vértices válidos)
- 📊 **Cálculo dos graus** (grau total, de entrada e de saída)
- 🔗 **Densidade** do grafo
- 🧠 **Algoritmo de Floyd-Warshall** para cálculo de caminhos mínimos
- 📐 **Matriz de distâncias e predecessores**
- 📏 **Cálculo do diâmetro**
- 📈 **Caminho médio entre todos os pares de vértices**
- 👤 **Cálculo de intermediação (betweenness)** por vértice
- 📃 **Exibição de métricas** detalhadas do grafo

## ▶️ Como Executar

1. Certifique-se de ter o Python instalado (versão 3.6+).
2. Execute o script no terminal:

```bash
python nome_do_arquivo.py
```

3. Insira o caminho do arquivo `.dat` quando solicitado.

## 📌 Exemplo de Uso

```text
Informe o caminho do arquivo .dat para leitura do grafo: exemplos/grafo.dat
Grafo validado com sucesso.
Densidade do grafo: 0.1234
Diâmetro do grafo: 7
Caminho médio: 3.2846
...
```

## 🛠️ Tecnologias Utilizadas

- Python 3
- Biblioteca `numpy` (pode ser retirada se não for usada em futuras etapas)

## 📌 Observações

- O programa lida com grafos mistos (com arestas não direcionadas e arcos direcionados).
- As informações de serviço e demanda são armazenadas, mas ainda não utilizadas em todos os cálculos — serão importantes para etapas futuras.

## 📚 Próximas Etapas (Planejamento)

- Implementar algoritmos de roteamento considerando custos e demandas.
- Análise de componentes fortemente conexos.
- Visualização gráfica dos grafos.
