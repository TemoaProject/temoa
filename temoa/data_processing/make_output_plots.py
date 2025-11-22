from __future__ import annotations

import argparse
import os
import random
import sqlite3
import sys
from collections.abc import Callable
from typing import TYPE_CHECKING, cast

import matplotlib
from matplotlib import cm as cmx
from matplotlib import colors
from matplotlib import pyplot as plt

if TYPE_CHECKING:
    from matplotlib.figure import Figure
    from matplotlib.legend import Legend

matplotlib.use('Agg')

# Type aliases for clarity using modern built-in generics
DbRow = list[str | int | float]
# All numeric lists are floats for consistency in plotting data.
PlotData = dict[str, list[float]]
Color = tuple[float, float, float, float]
ColorMapFunc = Callable[[int | float], Color]


class OutputPlotGenerator:
    """Generates plots from Temoa model output databases."""

    db_path: str
    region: str
    scenario: str
    folder_name: str
    output_file_name: str
    capacity_output: list[DbRow]
    output_vflow: list[DbRow]
    output_emissions: list[DbRow]
    tech_categories: list[list[str]]

    def __init__(
        self, path_to_db: str, region: str, scenario: str, super_categories: bool = False
    ) -> None:
        self.db_path = os.path.abspath(path_to_db)
        self.region = '%' if region == 'global' else region
        self.scenario = scenario
        self.folder_name = (
            f'{os.path.splitext(os.path.basename(path_to_db))[0]}_{region}_{scenario}_plots'
        )
        self.capacity_output = []
        self.output_vflow = []
        self.output_emissions = []
        self.tech_categories = []
        self.output_file_name = ''

    def extract_from_database(self, mode: int) -> None:
        """
        Based on the type of the plot being generated, extract data from the
        corresponding table from the database.
        """
        con = sqlite3.connect(self.db_path)
        cur = con.cursor()
        if mode == 1:
            cur.execute(
                f'SELECT sector, period, tech, capacity FROM output_net_capacity '
                f"WHERE scenario == '{self.scenario}' AND region LIKE '{self.region}'"
            )
            self.capacity_output = [list(elem) for elem in cur.fetchall()]
        elif mode == 2:
            cur.execute(
                f'SELECT sector, period, tech, SUM(flow) FROM output_flow_out '
                f"WHERE scenario == '{self.scenario}' AND region LIKE '{self.region}' "
                f'GROUP BY sector, period, tech'
            )
            self.output_vflow = [list(elem) for elem in cur.fetchall()]
        elif mode == 3:
            cur.execute(
                f'SELECT sector, period, emis_comm, SUM(emission) FROM output_emission '
                f"WHERE scenario == '{self.scenario}' AND region LIKE '{self.region}' "
                f'GROUP BY sector, period, emis_comm'
            )
            self.output_emissions = [list(elem) for elem in cur.fetchall()]

        cur.execute('SELECT tech, category FROM Technology')
        self.tech_categories = [[str(word) for word in t] for t in cur.fetchall()]
        con.close()

    def get_sectors(self, plot_type: int) -> list[str]:
        """
        Based on the type of the plot, returns a list of sectors available in the database.
        """
        self.extract_from_database(plot_type)
        sectors: set[str] = set()
        data: list[DbRow] = []

        if plot_type == 1:
            data = self.capacity_output
        elif plot_type == 2:
            data = self.output_vflow
        elif plot_type == 3:
            data = self.output_emissions

        for row in data:
            sectors.add(str(row[0]))

        res = sorted(sectors)
        res.insert(0, 'all')
        return res

    def process_data(
        self, input_data: list[DbRow], sector: str, super_categories: bool
    ) -> PlotData:
        """Processes data for a particular sector to make it ready for plotting."""
        periods_set: set[int] = set()
        techs_set: set[str] = set()

        for row in input_data:
            row[0] = str(row[0])
            row[1] = int(row[1])
            row[2] = str(row[2])
            row[3] = float(row[3])

        tech_dict = dict(self.tech_categories)
        if super_categories:
            for row in input_data:
                row[2] = tech_dict.get(str(row[2]), str(row[2]))

        for row in input_data:
            if row[0] == sector or sector == 'all':
                periods_set.add(int(row[1]))
                techs_set.add(str(row[2]))

        periods = sorted(periods_set)
        techs = sorted(techs_set)

        output_values: PlotData = {}
        for tech in techs:
            if tech in ('None', ''):
                continue
            output_values[tech] = [0.0] * len(periods)

        for row in input_data:
            tech_name = str(row[2])
            if tech_name not in output_values:
                continue
            if row[0] == sector or sector == 'all':
                output_values[tech_name][periods.index(int(row[1]))] += float(row[-1])

        output_values['periods'] = [float(p) for p in periods]
        return output_values

    def handle_output_path(
        self, plot_type: str, sector: str, super_categories: bool, output_dir: str
    ) -> str:
        """Constructs and creates the output path for the plot."""
        outfile = f'{plot_type}_{sector}'
        if super_categories:
            outfile += '_merged'
        outfile += '.png'

        full_output_dir = os.path.join(output_dir, self.folder_name)
        if not os.path.exists(full_output_dir):
            os.makedirs(full_output_dir)

        self.output_file_name = os.path.join(full_output_dir, outfile).replace(' ', '')
        return os.path.join(self.folder_name, outfile)

    def generate_plot_for_capacity(
        self, sector: str, super_categories: bool = False, output_dir: str = '.'
    ) -> str:
        """Generates a plot for the capacity of a given sector."""
        relative_path = self.handle_output_path('capacity', sector, super_categories, output_dir)
        if os.path.exists(self.output_file_name):
            print('not generating new capacity plot')
            return relative_path

        sectors = self.get_sectors(1)
        if sector not in sectors:
            return ''

        output_values = self.process_data(self.capacity_output, sector, super_categories)
        title = (
            f'Capacity Plot for {sector} across all regions'
            if self.region == '%'
            else f'Capacity Plot for {sector} sector in region {self.region}'
        )
        self.make_stacked_bar_plot(output_values, 'Years', 'Capacity', 'periods', title)
        return relative_path

    def generate_plot_for_output_flow(
        self, sector: str, super_categories: bool = False, output_dir: str = '.'
    ) -> str:
        """Generates a plot for the output flow of a given sector."""
        relative_path = self.handle_output_path('flow', sector, super_categories, output_dir)
        if os.path.exists(self.output_file_name):
            print('not generating new flow plot')
            return relative_path

        sectors = self.get_sectors(2)
        if sector not in sectors:
            return ''

        output_values = self.process_data(self.output_vflow, sector, super_categories)
        title = (
            f'Output Flow Plot for {sector} across all regions'
            if self.region == '%'
            else f'Output Flow Plot for {sector} sector in region {self.region}'
        )
        self.make_stacked_bar_plot(output_values, 'Years', 'Activity', 'periods', title)
        return relative_path

    def generate_plot_for_emissions(
        self, sector: str, super_categories: bool = False, output_dir: str = '.'
    ) -> str:
        """Generates a plot for the emissions of a given sector."""
        relative_path = self.handle_output_path('emissions', sector, super_categories, output_dir)
        if os.path.exists(self.output_file_name):
            print('not generating new emissions plot')
            return relative_path

        sectors = self.get_sectors(3)
        if sector not in sectors:
            return ''

        output_values = self.process_data(self.output_emissions, sector, super_categories)
        title = (
            f'Emissions Plot for {sector} across all regions'
            if self.region == '%'
            else f'Emissions Plot for {sector} sector in region {self.region}'
        )
        self.make_line_plot(output_values.copy(), 'Emissions', title)
        return relative_path

    # --------------------------- Plot Generation related functions ------------------------------

    def get_cmap(self, size: int) -> ColorMapFunc:
        """Returns a function that maps an index to a distinct RGB color."""
        color_norm = colors.Normalize(vmin=0, vmax=size - 1)
        scalar_map = cmx.ScalarMappable(norm=color_norm, cmap='viridis')

        def wrapper(index: int | float) -> Color:
            # We ignore the arg-type error. Mypy expects a NumPy array based on the
            # library's type stubs, but matplotlib's to_rgba function correctly
            # handles scalar inputs at runtime. This is a known limitation of the stubs.
            rgba_value = scalar_map.to_rgba(index)  # type: ignore[arg-type]
            return cast('Color', rgba_value)

        return wrapper

    def make_stacked_bar_plot(
        self, data: PlotData, xlabel: str, ylabel: str, xvar: str, title: str
    ) -> None:
        """Creates and saves a stacked bar plot."""
        random.seed(10)
        data_copy = data.copy()

        xaxis = data_copy.pop(xvar, [])
        data_copy.pop('c', None)
        stacked_bars = list(data_copy.keys())

        fig: Figure = plt.figure()
        cmap = self.get_cmap(len(stacked_bars))
        color_map_for_bars = {bar_name: cmap(i) for i, bar_name in enumerate(stacked_bars)}

        width = (
            min(xaxis[i + 1] - xaxis[i] for i in range(len(xaxis) - 1)) / 2.0
            if len(xaxis) > 1
            else 1.0
        )

        bottom = [0.0] * len(xaxis)
        handles = []
        for bar in stacked_bars:
            values = data_copy[bar]
            h = plt.bar(xaxis, values, width, bottom=bottom, color=color_map_for_bars[bar])
            handles.append(h)
            bottom = [b + v for b, v in zip(bottom, values, strict=False)]

        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        plt.xticks(xaxis, [str(int(x)) for x in xaxis])
        plt.title(title)
        lgd: Legend = plt.legend(
            [h[0] for h in handles], stacked_bars, bbox_to_anchor=(1.2, 1), fontsize=7.5
        )
        plt.savefig(self.output_file_name, bbox_extra_artists=(lgd,), bbox_inches='tight')
        plt.close(fig)

    def make_line_plot(self, plot_var: PlotData, label: str, title: str) -> None:
        """Creates and saves a line plot."""
        random.seed(10)

        periods = plot_var.pop('periods', [])
        techs = list(plot_var.keys())

        fig: Figure = plt.figure()
        cmap = self.get_cmap(len(techs))
        color_map = {tech: cmap(i) for i, tech in enumerate(techs)}

        handles = []
        for tech in techs:
            values = plot_var[tech]
            h = plt.plot(periods, values, color=color_map[tech], linestyle='--', marker='o')
            handles.append(h)

        plt.xlabel('Years')
        plt.ylabel(label)
        plt.xticks(periods, [str(int(p)) for p in periods])
        plt.title(title)
        lgd: Legend = plt.legend(
            [h[0] for h in handles], techs, bbox_to_anchor=(1.2, 1), fontsize=7.5
        )
        plt.savefig(self.output_file_name, bbox_extra_artists=(lgd,), bbox_inches='tight')
        plt.close(fig)


def generate_plot(args: list[str]) -> None:
    """Parses command line arguments and calls relevant functions."""
    parser = argparse.ArgumentParser(description='Generate Output Plot')
    parser.add_argument(
        '-i',
        '--input',
        action='store',
        dest='input',
        help='Input Database Filename <path>',
        required=True,
    )
    parser.add_argument(
        '-r',
        '--region',
        action='store',
        dest='region',
        help="Region name, input 'global' if global results are desired",
        required=True,
    )
    parser.add_argument(
        '-s',
        '--scenario',
        action='store',
        dest='scenario',
        help='Model run a scenario name',
        required=True,
    )
    parser.add_argument(
        '-p',
        '--plot-type',
        action='store',
        dest='type',
        help='Type of Plot to be generated',
        choices=['capacity', 'flow', 'emissions'],
        required=True,
    )
    parser.add_argument(
        '-c',
        '--sector',
        action='store',
        dest='sector',
        help='Sector for which plot to be generated',
        required=True,
    )
    parser.add_argument(
        '-o',
        '--output',
        action='store',
        dest='output_dir',
        help='Output plot location',
        default='./',
    )
    parser.add_argument(
        '--super',
        action='store_true',
        dest='super_categories',
        help='Merge Technologies or not',
        default=False,
    )

    options = parser.parse_args(args)
    result_generator = OutputPlotGenerator(
        options.input, options.region, options.scenario, options.super_categories
    )

    error_path = ''
    if options.type == 'capacity':
        error_path = result_generator.generate_plot_for_capacity(
            options.sector, options.super_categories, options.output_dir
        )
    elif options.type == 'flow':
        error_path = result_generator.generate_plot_for_output_flow(
            options.sector, options.super_categories, options.output_dir
        )
    elif options.type == 'emissions':
        error_path = result_generator.generate_plot_for_emissions(
            options.sector, options.super_categories, options.output_dir
        )

    if not error_path:
        print("Error: The sector doesn't exist for the selected plot type and database.")
    else:
        full_path = os.path.join(options.output_dir, os.path.dirname(error_path))
        print(f'Done. Look for output plot images in directory: {os.path.abspath(full_path)}')


if __name__ == '__main__':
    generate_plot(sys.argv[1:])
