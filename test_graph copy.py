import dask.dataframe as dd
import networkx as nx
import time
import os
from pyvis.network import Network
import matplotlib.pyplot as plt
import numpy as np
from collections import Counter
from IPython.display import display, HTML
import pandas as pd  # Adicionado para manipulação de datas


def convert_to_parquet_if_needed():
    """Converte APENAS o arquivo CSV de links para Parquet se necessário"""
    csv_links_path = "static/dataset/bitcoin.links.csv"
    parquet_links_path = csv_links_path.replace(".csv", ".parquet")

    os.makedirs(os.path.dirname(parquet_links_path), exist_ok=True)

    if not os.path.exists(parquet_links_path):
        print(f"Convertendo {csv_links_path} para Parquet...")
        links = dd.read_csv(csv_links_path)
        links.to_parquet(parquet_links_path)
        print(f"Arquivo Parquet salvo em: {parquet_links_path}")
    else:
        print(f"Arquivo Parquet já existe: {parquet_links_path}")


def load_datasets():
    """Carrega APENAS os links no formato Parquet"""
    parquet_links_path = "static/dataset/bitcoin.links.parquet"
    return dd.read_parquet(parquet_links_path)


def filter_data(links, start_date, end_date):
    """
    Filtra os links pelo intervalo de datas
    Versão otimizada para trabalhar com Parquet
    """
    # Converter as datas de filtro para datetime64[ns]
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)

    # Garantir que a coluna mindate está no formato datetime
    links["mindate"] = dd.to_datetime(links["mindate"], format="%Y%m%dT%H%M%S")

    # Aplicar o filtro
    filtered_links = links[
        (links["mindate"] >= start_date) & (links["mindate"] <= end_date)
    ].compute()

    return filtered_links


def create_graph(filtered_links):
    """Cria um grafo direcionado apenas com os dados das arestas (links)"""
    G = nx.DiGraph()

    # Converter IDs para string
    filtered_links["src_id"] = filtered_links["src_id"].astype(str)
    filtered_links["dst_id"] = filtered_links["dst_id"].astype(str)

    # Adicionar arestas com atributos
    for _, row in filtered_links.iterrows():
        G.add_edge(
            row["src_id"],
            row["dst_id"],
            weight=row["count"],
            title=f"Transações: {row['count']}",
            mindate=str(row["mindate"]),
            maxdate=str(row["maxdate"]),
        )
    return G


def visualize_graph_interactive(G, output_file="graph_interactive.html", num_nodes=300):
    """Visualização interativa otimizada"""
    net = Network(
        notebook=True,
        height="750px",
        width="100%",
        directed=True,
        bgcolor="#222222",
        font_color="white",
        cdn_resources="remote",
    )

    # Configuração de layout
    net.force_atlas_2based(
        gravity=-50,
        central_gravity=0.01,
        spring_length=100,
        spring_strength=0.08,
        damping=0.4,
        overlap=1,
    )

    # Selecionar nós mais importantes
    nodes_sorted = sorted(
        G.nodes(), key=lambda x: G.degree(x, weight="weight"), reverse=True
    )
    subgraph = G.subgraph(nodes_sorted[:num_nodes])

    # Adicionar nós
    degrees = dict(subgraph.degree(weight="weight"))
    for node in subgraph.nodes():
        net.add_node(
            node,
            label=str(node),
            size=10 + np.log(degrees[node] + 1) * 3,
            color="#4ECDC4",  # Cor única já que não temos tipos
            title=f"Nó: {node}\nGrau: {degrees[node]}",
        )

    # Adicionar arestas
    for u, v, data in subgraph.edges(data=True):
        net.add_edge(
            u,
            v,
            width=0.5 + np.log(data.get("weight", 1) + 1) * 0.3,
            title=f"Transações: {data.get('weight', 1)}\nPeríodo: {data.get('mindate', '')} a {data.get('maxdate', '')}",
            color="#97C2FC",
        )

    # Salvar e exibir
    output_path = f"templates/{output_file}"
    os.makedirs(
        os.path.dirname(output_path), exist_ok=True
    )  # Garante que o diretório existe
    net.save_graph(output_path)
    print(f"Visualização salva em: {output_path}")

    # Para exibir no notebook
    display(HTML(output_path))


def analyze_bitcoin_network(G):
    """Análise focada apenas nas propriedades da rede de transações"""
    print("\n" + "=" * 80)
    print("ANÁLISE DA REDE DE TRANSAÇÕES".center(80))
    print("=" * 80)

    # Informações básicas
    print(f"\nNós: {G.number_of_nodes()}")
    print(f"Arestas: {G.number_of_edges()}")

    # Componentes conectados
    wcc = list(nx.weakly_connected_components(G))
    print(f"\nComponentes conectados: {len(wcc)}")
    print(f"Maior componente: {len(max(wcc, key=len))} nós")

    # Distribuição de grau
    degrees = [d for _, d in G.degree(weight="weight")]
    print("\nDistribuição de grau:")
    print(f"Média: {np.mean(degrees):.1f}")
    print(f"Máximo: {max(degrees)}")

    # Centralidades (apenas degree para performance)
    print("\nTop nós por grau:")
    for node, deg in sorted(
        G.degree(weight="weight"), key=lambda x: x[1], reverse=True
    )[:5]:
        print(f"{node}: {deg} transações")


if __name__ == "__main__":
    print("Iniciando processamento...")
    try:
        # 1. Conversão para Parquet
        convert_to_parquet_if_needed()

        # 2. Carregar dados
        print("\nCarregando dados...")
        links = load_datasets()

        # 3. Definir período
        start_date = "2012-01-01"
        end_date = "2012-01-31"

        # 4. Filtrar
        print(f"\nFiltrando de {start_date} a {end_date}...")
        filtered_links = filter_data(links, start_date, end_date)
        print(f"Transações encontradas: {len(filtered_links)}")

        if len(filtered_links) == 0:
            raise ValueError("Nenhuma transação no período.")

        # 5. Criar grafo
        print("\nCriando grafo...")
        start_time = time.time()
        G = create_graph(filtered_links)
        print(f"Grafo criado em {time.time() - start_time:.2f}s")

        # 6. Visualização
        print("\nGerando visualização...")
        visualize_graph_interactive(G)

        # 7. Análise
        print("\nAnalisando rede...")
        analyze_bitcoin_network(G)

    except Exception as e:
        print(f"\nErro: {str(e)}")
        import traceback

        traceback.print_exc()
