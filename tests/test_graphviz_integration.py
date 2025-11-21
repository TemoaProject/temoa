from __future__ import annotations

import shutil
import tempfile
import unittest
from pathlib import Path
from typing import cast
from unittest.mock import MagicMock, patch

from temoa.core.config import TemoaConfig
from temoa.model_checking.commodity_graph import generate_graphviz_files, visualize_graph
from temoa.model_checking.network_model_data import NetworkModelData
from temoa.types.core_types import Commodity, Period, Region, Sector, Technology, Vintage
from temoa.utilities.graph_utils import EdgeTuple


class TestGraphvizIntegration(unittest.TestCase):
    def setUp(self) -> None:  # noqa: N802
        # Create a unique temp output directory per test run
        self._tmp_dir = Path(tempfile.mkdtemp(prefix='temoa_test_output_'))

        self.config = MagicMock(spec=TemoaConfig)
        self.config.plot_commodity_network = True
        self.config.graphviz_output = True
        self.config.output_path = self._tmp_dir

        self.network_data = MagicMock(spec=NetworkModelData)

        self.network_data.available_techs = {
            (cast(Region, 'region'), cast(Period, '2020')): {('tech1', 'v1')}
        }
        self.network_data.source_commodities = {
            (cast(Region, 'region'), cast(Period, '2020')): {'coal'}
        }
        self.network_data.demand_commodities = {
            (cast(Region, 'region'), cast(Period, '2020')): {'electricity'}
        }

        self.edge_tuple = EdgeTuple(
            region=cast(Region, 'region'),
            tech=cast(Technology, 'tech1'),
            vintage=cast(Vintage, 'v1'),
            input_comm=cast(Commodity, 'coal'),
            output_comm=cast(Commodity, 'electricity'),
            sector=cast(Sector, 'electric'),
        )

    def tearDown(self) -> None:  # noqa: N802
        shutil.rmtree(self._tmp_dir, ignore_errors=True)

    @patch('temoa.model_checking.commodity_graph.generate_commodity_graph')
    @patch('temoa.model_checking.commodity_graph.generate_technology_graph')
    @patch('temoa.model_checking.commodity_graph.nx_to_vis')
    @patch('temoa.model_checking.commodity_graph.generate_graphviz_files')
    def test_visualize_graph_calls_graphviz(
        self,
        mock_gen_gv: MagicMock,
        mock_nx_vis: MagicMock,
        mock_gen_tech: MagicMock,
        mock_gen_comm: MagicMock,
    ) -> None:
        mock_gen_comm.return_value = (MagicMock(), {})
        mock_gen_tech.return_value = MagicMock()
        mock_nx_vis.return_value = 'path/to/graph.html'

        visualize_graph(
            region=cast(Region, 'region'),
            period=cast(Period, '2020'),
            network_data=self.network_data,
            demand_orphans=[],
            other_orphans=[],
            driven_techs=[self.edge_tuple],
            config=self.config,
        )

        mock_gen_gv.assert_called_once()
        args, _ = mock_gen_gv.call_args
        self.assertEqual(args[0], '2020')
        self.assertEqual(args[1], 'region')
        # Check that output path is passed correctly
        self.assertEqual(args[5], self.config.output_path)

    @patch('subprocess.call')
    def test_generate_graphviz_files_creates_dot_file(self, mock_subprocess: MagicMock) -> None:
        with tempfile.TemporaryDirectory(prefix='temoa_test_output_') as tmp_output_dir_str:
            output_dir = Path(tmp_output_dir_str)

            sector_colors = {cast(Sector, 'electric'): 'blue'}
            all_techs = [self.edge_tuple]

            generate_graphviz_files(
                period=cast(Period, '2020'),
                region=cast(Region, 'region'),
                network_data=self.network_data,
                all_techs=all_techs,
                sector_colors=sector_colors,
                output_dir=output_dir,
            )

            dot_file = output_dir / 'results_region_2020.dot'
            self.assertTrue(dot_file.exists())

            with open(dot_file) as f:
                content = f.read()
                self.assertIn('label = "Results for 2020"', content)
                self.assertIn('label="tech1"', content)
                self.assertIn('label="coal"', content)
                self.assertIn('label="electricity"', content)

            # Verify subprocess call
            svg_file = output_dir / 'results_region_2020.svg'
            mock_subprocess.assert_called_with(['dot', '-Tsvg', f'-o{svg_file}', str(dot_file)])


if __name__ == '__main__':
    unittest.main()
