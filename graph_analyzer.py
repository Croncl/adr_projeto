import dask.dataframe as dd
import networkx as nx
import pandas as pd
import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pyvis.network import Network
import os


class BitcoinGraphAnalyzer:
    def __init__(self):
        self.graph = None
        self.analysis_results = {}

    def run_full_analysis(self, start_date="2012-01-01", end_date="2012-01-31"):
        """Executa todo o pipeline de análise"""
        # 1. Carregar dados
        links = self.load_data()

        # 2. Filtrar
        filtered = self.filter_data(links, start_date, end_date)

        # 3. Criar grafo
        self.graph = self.create_graph(filtered)

        # 4. Gerar visualizações
        self.generate_visualizations()

        return self.analysis_results

    def load_data(self):
        """Carrega os dados do Parquet"""
        parquet_path = "static/dataset/bitcoin.links.parquet"
        if not os.path.exists(parquet_path):
            self.convert_to_parquet()
        return dd.read_parquet(parquet_path)

    def convert_to_parquet(self):
        """Converte CSV para Parquet se necessário"""
        csv_path = "static/dataset/bitcoin.links.csv"
        parquet_path = csv_path.replace(".csv", ".parquet")

        os.makedirs(os.path.dirname(parquet_path), exist_ok=True)

        print(f"Convertendo {csv_path} para Parquet...")
        dd.read_csv(csv_path).to_parquet(parquet_path)
        print(f"Parquet salvo em: {parquet_path}")

    def filter_data(self, links, start_date, end_date):
        """Filtra os dados por período"""
        start_date = pd.to_datetime(start_date)
        end_date = pd.to_datetime(end_date)

        links["mindate"] = dd.to_datetime(links["mindate"], format="%Y%m%dT%H%M%S")
        return links[
            (links["mindate"] >= start_date) & (links["mindate"] <= end_date)
        ].compute()

    def create_graph(self, filtered_links):
        """Cria o grafo NetworkX"""
        G = nx.DiGraph()
        filtered_links["src_id"] = filtered_links["src_id"].astype(str)
        filtered_links["dst_id"] = filtered_links["dst_id"].astype(str)

        for _, row in filtered_links.iterrows():
            G.add_edge(
                row["src_id"],
                row["dst_id"],
                weight=row["count"],
                mindate=str(row["mindate"]),
                maxdate=str(row["maxdate"]),
            )
        return G

    def generate_visualizations(self):
        """Gera todas as visualizações"""
        # 1. Gráfico de distribuição de grau (para o blog)
        self._generate_degree_plot()

        # 1b. Boxplot dos graus dos nós
        self._generate_boxplot_degree()

        # 2. Grafo interativo (para visualizations.html)
        self._generate_interactive_graph()

        # 3. Métricas para o blog
        self.analysis_results = {
            "num_nodes": self.graph.number_of_nodes(),
            "num_edges": self.graph.number_of_edges(),
            "top_nodes": sorted(
                self.graph.degree(weight="weight"), key=lambda x: x[1], reverse=True
            )[:5],
            "graph_image": "static/images/degree_dist.png",
        }

    def _generate_degree_plot(self):
        """Gera o gráfico de distribuição de grau"""
        degrees = [d for _, d in self.graph.degree(weight="weight")]
        plt.figure(figsize=(10, 6))
        plt.hist(degrees, bins=50, color="skyblue", log=True)
        plt.title("Distribuição de Grau das Transações")
        plt.xlabel("Número de Transações")
        plt.ylabel("Contagem (log)")

        os.makedirs("static/images", exist_ok=True)
        plt.savefig("static/images/degree_dist.png")
        plt.close()

    def _generate_boxplot_degree(self):
        """Gera o boxplot dos graus dos nós (normalizado em log para melhor visualização)"""
        degrees = [d for _, d in self.graph.degree(weight="weight")]
        # Normalização logarítmica para melhor visualização
        degrees_log = np.log1p(degrees)  # log(1 + x) para evitar log(0)
        plt.figure(figsize=(10, 4))
        box = plt.boxplot(
            degrees_log,
            vert=False,
            patch_artist=True,
            boxprops=dict(facecolor="skyblue", color="blue"),
            medianprops=dict(color="red", linewidth=2),
            flierprops=dict(
                markerfacecolor="orange",
                marker="o",
                markersize=6,
                linestyle="none",
                markeredgecolor="gray",
            ),
        )
        plt.title("Boxplot dos Graus dos Nós (escala logarítmica)")
        plt.xlabel("log(1 + Grau) (número de transações)")
        # Adiciona legenda personalizada
        from matplotlib.lines import Line2D

        legend_elements = [
            Line2D([0], [0], color="red", lw=2, label="Mediana"),
            Line2D(
                [0],
                [0],
                marker="o",
                color="w",
                label="Outliers",
                markerfacecolor="orange",
                markersize=8,
                markeredgecolor="gray",
            ),
            Line2D([0], [0], color="blue", lw=2, label="Boxplot"),
        ]
        plt.legend(handles=legend_elements, loc="upper right")
        os.makedirs("static/images", exist_ok=True)
        plt.tight_layout()
        plt.savefig("static/images/degree_boxplot.png")
        plt.close()

    def _generate_interactive_graph(self, num_nodes=300):
        """Gera o grafo interativo com PyVis"""
        net = Network(
            height="750px",
            width="100%",
            directed=True,
            notebook=False,
            bgcolor="#222222",
            font_color="white",
            cdn_resources="remote",
        )

        net.toggle_physics(True)
        net.force_atlas_2based(
            gravity=-100,
            central_gravity=0.005,
            spring_length=200,
            spring_strength=0.05,
            damping=0.4,
        )

        highlight_options = """
        {
        "interaction": {
            "hover": true,
            "multiselect": true,
            "selectConnectedEdges": true,
            "navigationButtons": true
        },
        "edges": {
            "color": {
            "inherit": false,
            "color": "#97C2FC",
            "highlight": "#ff9800",
            "hover": "#00ff00"
            },
            "selectionWidth": 4,
            "arrows": {
            "to": { "enabled": true, "scaleFactor": 1 }
            }
        },
        "nodes": {
            "borderWidth": 2,
            "borderWidthSelected": 4,
            "color": {
            "highlight": "#ff0",
            "hover": "#0ff"
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
        net.set_options(highlight_options)

        # Selecionar nós mais importantes
        nodes_sorted = sorted(
            self.graph.nodes(),
            key=lambda x: self.graph.degree(x, weight="weight"),
            reverse=True,
        )
        subgraph = self.graph.subgraph(nodes_sorted[:num_nodes])

        # Adiciona nós com cores baseadas no grau
        degrees = dict(subgraph.degree())
        for node in subgraph.nodes():
            net.add_node(
                node,
                label=str(node),
                size=10 + degrees[node] * 0.7,
                color=f"hsl({240 - degrees[node]*7}, 75%, 50%)",
                title=f"Nó: {node} (Grau: {degrees[node]})",
            )

        # Adiciona arestas
        for u, v, data in subgraph.edges(data=True):
            weight = data.get("weight", 1.0)
            net.add_edge(
                u,
                v,
                width=0.5 + float(weight) * 0.01,
                title=f"Peso: {weight:.2f}",
                color="#97C2FC",
            )

        # Salvar no output
        os.makedirs("static/visualizations", exist_ok=True)
        output_path = "static/visualizations/graph_output.html"
        net.save_graph(output_path)
