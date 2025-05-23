import pandas as pd
import networkx as nx
from flask import render_template
from main import app

# Função para carregar os datasets
def load_datasets():
    links_path = "static/dataset/bitcoin.links.csv"
    vertices_path = "static/dataset/bitcoin.vertices.csv"
    
    # Carregar os arquivos CSV
    links = pd.read_csv(links_path)
    vertices = pd.read_csv(vertices_path)
    
    return links, vertices

# Função para criar o grafo
def create_graph():
    links, vertices = load_datasets()
    
    # Usar os nomes corretos das colunas
    source_column = 'src_id'  # Coluna de origem
    target_column = 'dst_id'  # Coluna de destino
    weight_column = 'count'   # Coluna de peso (número de transações)
    
    # Criar o grafo direcionado
    G = nx.DiGraph()
    
    # Adicionar nós
    G.add_nodes_from(vertices['vid'])  # Certifique-se de que a coluna 'id' existe no arquivo vertices.csv
    
    # Adicionar arestas
    for _, row in links.iterrows():
        G.add_edge(row[source_column], row[target_column], weight=row[weight_column])
    
    return G

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/blog")
def blog():
    return render_template("blog.html")

@app.route("/visualizations")
def visualizations():
    # Criar o grafo
    G = create_graph()
    
    # Calcular métricas
    num_vertices = G.number_of_nodes()
    num_links = G.number_of_edges()
    
    return render_template(
        "visualizations.html",
        num_vertices=num_vertices,
        num_links=num_links
    )