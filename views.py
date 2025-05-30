from flask import render_template
from app import app
from graph_analyzer import BitcoinGraphAnalyzer


@app.route("/")
def home():
    return render_template("home.html")


@app.route("/blog")
def blog():
    analyzer = BitcoinGraphAnalyzer()
    results = analyzer.run_full_analysis()
    return render_template("blog.html", results=results)


@app.route("/visualizations")
def visualizations():
    analyzer = BitcoinGraphAnalyzer()
    analyzer.run_full_analysis()  # Gera o gráfico
    return render_template(
        "visualizations.html",
        num_nodes=analyzer.graph.number_of_nodes(),
        num_edges=analyzer.graph.number_of_edges(),
    )
