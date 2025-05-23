import dask.dataframe as dd
import networkx as nx
import time
from pyvis.network import Network

def load_datasets():
    links_path = "adr_projeto/static/dataset/bitcoin.links.csv"
    vertices_path = "adr_projeto/static/dataset/bitcoin.vertices.csv"
    
    # Carregar os arquivos CSV usando Dask
    links = dd.read_csv(links_path)
    vertices = dd.read_csv(vertices_path)
    
    return links, vertices

def filter_links_by_date(links, start_date, end_date):
    # Converter as colunas de data para o formato datetime, especificando o formato
    date_format = "%Y%m%dT%H%M%S"  # Formato das datas no dataset
    links['mindate'] = dd.to_datetime(links['mindate'], format=date_format)
    links['maxdate'] = dd.to_datetime(links['maxdate'], format=date_format)
    
    # Filtrar as transações dentro do intervalo de datas
    filtered_links = links[(links['mindate'] >= start_date) & (links['maxdate'] <= end_date)]
    return filtered_links.compute()  # Converte o resultado para um DataFrame Pandas

def create_graph(filtered_links, vertices):
    # Usar os nomes corretos das colunas
    source_column = 'src_id'  # Coluna de origem
    target_column = 'dst_id'  # Coluna de destino
    weight_column = 'count'   # Coluna de peso (número de transações)
    node_column = 'vid'       # Coluna de identificação dos nós
    
    # Criar o grafo direcionado
    G = nx.DiGraph()
    
    # Adicionar nós
    vertices = vertices.compute()  # Converte para Pandas para iteração
    G.add_nodes_from(vertices[node_column])
    
    # Adicionar arestas em partes
    for _, row in filtered_links.iterrows():
        G.add_edge(row[source_column], row[target_column], weight=row[weight_column])
    
    return G

def visualize_graph_interactive(G, output_file="graph_interactive.html", num_nodes=500):
    # Criar um subgrafo com os primeiros `num_nodes` nós
    subgraph = G.subgraph(list(G.nodes)[:num_nodes])
    
    # Criar a visualização interativa com Pyvis
    net = Network(height="750px", width="100%", directed=True)
    net.from_nx(subgraph)
    
    # Configurar opções de física para a visualização
    net.show_buttons(filter_=['physics'])
    net.show(output_file)
    print(f"Visualização interativa salva em: {output_file}")

if __name__ == "__main__":
    print("Carregando os datasets...")
    try:
        # Carregar os datasets
        links, vertices = load_datasets()
        
        # Definir o intervalo de datas para filtrar
        start_date = "2012-01-01"
        end_date = "2012-01-02"
        
        print(f"Filtrando links entre {start_date} e {end_date}...")
        filtered_links = filter_links_by_date(links, start_date, end_date)
        print(f"Número de links após o filtro: {len(filtered_links)}")
        
        # Medir o tempo de geração do grafo
        start_time = time.time()
        G = create_graph(filtered_links, vertices)
        end_time = time.time()
        
        print("Grafo gerado com sucesso!")
        print(f"Número de Nós: {G.number_of_nodes()}")
        print(f"Número de Arestas: {G.number_of_edges()}")
        print(f"Tempo de geração do grafo: {end_time - start_time:.2f} segundos")
        
        # Visualizar o grafo interativamente
        visualize_graph_interactive(G, num_nodes=500)  # Visualizar os primeiros 500 nós
    except Exception as e:
        print(f"Erro ao gerar o grafo: {e}")