import unittest
from graph_analyzer import BitcoinGraphAnalyzer
import pandas as pd


class GraphAnalyzerTestCase(unittest.TestCase):
    def test_create_graph(self):
        analyzer = BitcoinGraphAnalyzer()
        df = pd.DataFrame(
            {
                "src_id": ["a", "b"],
                "dst_id": ["b", "c"],
                "count": [1, 2],
                "mindate": ["2020-01-01", "2020-01-02"],
                "maxdate": ["2020-01-01", "2020-01-02"],
            }
        )
        G = analyzer.create_graph(df)
        self.assertEqual(G.number_of_nodes(), 3)
        self.assertEqual(G.number_of_edges(), 2)
