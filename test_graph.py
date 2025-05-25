import dask.dataframe as dd
import networkx as nx
import time
import os
import json
from pyvis.network import Network


def convert_to_parquet_if_needed():
    """Converte os arquivos CSV para Parquet se necessário, salvando na mesma pasta"""
    csv_links_path = "static/dataset/bitcoin.links.csv"
    csv_vertices_path = "static/dataset/bitcoin.vertices.csv"

    # Usar a mesma pasta dos CSVs para os Parquets
    parquet_links_path = csv_links_path.replace(".csv", ".parquet")
    parquet_vertices_path = csv_vertices_path.replace(".csv", ".parquet")

    # Criar diretório se não existir
    os.makedirs(os.path.dirname(parquet_links_path), exist_ok=True)

    # Converter links se necessário
    if not os.path.exists(parquet_links_path):
        print(f"Convertendo {csv_links_path} para Parquet...")
        links = dd.read_csv(csv_links_path)
        links.to_parquet(parquet_links_path)
        print(f"Arquivo Parquet salvo em: {parquet_links_path}")
    else:
        print(f"Arquivo Parquet já existe: {parquet_links_path}")

    # Converter vértices se necessário
    if not os.path.exists(parquet_vertices_path):
        print(f"Convertendo {csv_vertices_path} para Parquet...")
        vertices = dd.read_csv(csv_vertices_path)
        vertices.to_parquet(parquet_vertices_path)
        print(f"Arquivo Parquet salvo em: {parquet_vertices_path}")
    else:
        print(f"Arquivo Parquet já existe: {parquet_vertices_path}")


def load_datasets():
    """Carrega os datasets no formato Parquet"""
    parquet_links_path = "static/dataset/bitcoin.links.parquet"
    parquet_vertices_path = "static/dataset/bitcoin.vertices.parquet"

    # Carregar os arquivos Parquet usando Dask
    links = dd.read_parquet(parquet_links_path)
    vertices = dd.read_parquet(parquet_vertices_path)

    return links, vertices


def filter_data(links, vertices, start_date, end_date):
    """Filtra links e vértices pelo intervalo de datas"""
    # Converter datas para datetime
    date_format = "%Y%m%dT%H%M%S"

    # Filtrar links
    links["mindate"] = dd.to_datetime(links["mindate"], format=date_format)
    links["maxdate"] = dd.to_datetime(links["maxdate"], format=date_format)
    filtered_links = links[
        (links["mindate"] >= start_date) & (links["maxdate"] <= end_date)
    ].compute()

    # Filtrar vértices
    vertices["first_transaction_date"] = dd.to_datetime(
        vertices["first_transaction_date"], format=date_format
    )
    filtered_vertices = vertices[
        (vertices["first_transaction_date"] >= start_date)
        & (vertices["first_transaction_date"] <= end_date)
    ].compute()

    return filtered_links, filtered_vertices


def create_graph(filtered_links, filtered_vertices):
    """Cria um grafo direcionado a partir dos dados filtrados"""
    # Converter para string para evitar problemas de tipo
    filtered_links["src_id"] = filtered_links["src_id"].astype(str)
    filtered_links["dst_id"] = filtered_links["dst_id"].astype(str)
    filtered_vertices["vid"] = filtered_vertices["vid"].astype(str)

    G = nx.DiGraph()
    G.add_nodes_from(filtered_vertices["vid"])

    for _, row in filtered_links.iterrows():
        G.add_edge(
            str(row["src_id"]),
            str(row["dst_id"]),
            weight=row["count"],
            title=f"Transações: {row['count']}",
            mindate=str(row["mindate"]),
            maxdate=str(row["maxdate"]),
        )
    return G


def visualize_graph_interactive(G, output_file="graph_interactive.html", num_nodes=500):
    """Cria uma visualização interativa do grafo"""
    try:
        nodes_sorted_by_degree = sorted(
            G.nodes(), key=lambda x: G.degree(x), reverse=True
        )
        subgraph = G.subgraph(nodes_sorted_by_degree[:num_nodes])

        net = Network(
            height="700",
            width="95%",
            directed=True,
            notebook=False,
            bgcolor="#222222",
            font_color="white",
        )

        for node in subgraph.nodes():
            net.add_node(node, label=str(node), title=f"Nó: {node}")

        for edge in subgraph.edges(data=True):
            net.add_edge(edge[0], edge[1], value=edge[2].get("weight", 1))

        # Opções customizadas (ajustáveis pelo usuário no HTML)
        options = """
        {
        "configure": {
            "enabled": true,
            "filter": [
            "edges",
            "nodes"
            ]
        },
        "nodes": {
            "borderWidth": 1,
            "borderWidthSelected": 2,
            "opacity": 1,
            "size": 20
        },
        "edges": {
            "color": {
            "inherit": true
            },
            "selfReferenceSize": 30,
            "selfReference": {
            "angle": 0.5},
            "smooth": {
            "forceDirection": "none"
            }
        },
        "physics": {
            "forceAtlas2Based": {
            "springLength": 100
            },
            "minVelocity": 0.5,
            "solver": "forceAtlas2Based",
            "timestep": 0.08
        }
        }
        """
        net.set_options(options)

        net.write_html(output_file)  # Remova o argumento cdn_resources

        # Ajuste o CSS do #mynetwork para centralizar (opcional)
        with open(output_file, "r", encoding="utf-8") as f:
            html = f.read()

        import re

        html = re.sub(
            r"(#mynetwork\s*{[^}]+})",
            """#mynetwork {
    width: 100%;
    height: 700px;
    background-color: #222222;
    border: 1px solid lightgray;
    position: relative;
    padding: 1px;
    margin: auto auto auto auto;
}""",
            html,
        )

        with open(output_file, "w", encoding="utf-8") as f:
            f.write(html)

        print(f"Visualização interativa gerada com sucesso em: {output_file}")
        print(f"Abra o arquivo {output_file} em seu navegador para visualizar o grafo.")

    except Exception as e:
        print(f"Erro ao gerar visualização: {e}")
        raise


if __name__ == "__main__":
    print("Iniciando processamento...")
    try:
        # 1. Conversão para Parquet (se necessário)
        convert_to_parquet_if_needed()

        # 2. Carregar datasets
        print("Carregando os datasets em Parquet...")
        links, vertices = load_datasets()

        # 3. Definir intervalo de datas (ajustado para 1 mês para mais conexões)
        start_date = "2012-01-01"
        end_date = "2012-01-31"  # Período de 1 mês

        # 4. Filtrar dados (agora filtramos tanto links quanto vértices)
        print(f"\nFiltrando dados entre {start_date} e {end_date}...")
        filtered_links, filtered_vertices = filter_data(
            links, vertices, start_date, end_date
        )

        print(f"\nEstatísticas após filtro:")
        print(f"- Nós/vértices: {len(filtered_vertices)}")
        print(f"- Arestas/links: {len(filtered_links)}")

        if len(filtered_links) == 0:
            raise ValueError(
                "Nenhuma aresta encontrada no período selecionado. Tente ampliar o intervalo de datas."
            )

        # 5. Criar grafo e medir tempo
        print("\nCriando grafo...")
        start_time = time.time()
        G = create_graph(filtered_links, filtered_vertices)
        end_time = time.time()

        # 6. Remover nós isolados para melhor visualização
        isolated_nodes = list(nx.isolates(G))
        if isolated_nodes:
            print(f"Removendo {len(isolated_nodes)} nós isolados...")
            G.remove_nodes_from(isolated_nodes)

        print("\nGrafo gerado com sucesso!")
        print(f"- Número total de nós: {G.number_of_nodes()}")
        print(f"- Número total de arestas: {G.number_of_edges()}")
        print(f"- Tempo de geração: {end_time - start_time:.2f} segundos")

        # 7. Visualização interativa (com número reduzido de nós)
        print("\nGerando visualização interativa...")
        visualize_graph_interactive(
            G,
            output_file="bitcoin_network.html",
            num_nodes=min(300, G.number_of_nodes()),  # Máximo de 300 nós ou menos
        )

    except Exception as e:
        print(f"\nErro durante o processamento: {str(e)}")
        # Opcional: imprimir traceback completo para depuração
        import traceback

        traceback.print_exc()
