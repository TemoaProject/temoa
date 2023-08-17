import sqlite3, sys
import matplotlib

matplotlib.use("Agg")
from matplotlib import pyplot as plt, cm as cmx, colors
from IPython import embed as IP
import numpy as np
import random
import time
import os
import argparse


class OutputPlotGenerator:
    def __init__(self, path_to_db, region, scenario, super_categories=False):
        self.db_path = os.path.abspath(path_to_db)
        if region == "global":
            self.region = "%"
        else:
            self.region = region
        self.scenario = scenario
        self.folder_name = (
            os.path.splitext(os.path.basename(path_to_db))[0]
            + "_"
            + region
            + "_"
            + scenario
            + "_plots"
        )
        # self.extractFromDatabase()

    def extractFromDatabase(self, type):
        """
        Based on the type of the plot being generated, extract data from the corresponding table from database
        """
        con = sqlite3.connect(self.db_path)
        cur = con.cursor()
        if type == 1:
            cur.execute(
                "SELECT sector, t_periods, tech, capacity FROM Output_CapacityByPeriodAndTech WHERE scenario == '"
                + self.scenario
                + "' AND regions LIKE '"
                + self.region
                + "'"
            )
            self.capacity_output = cur.fetchall()
            self.capacity_output = [list(elem) for elem in self.capacity_output]
        elif type == 2:
            cur.execute(
                "SELECT sector, t_periods, tech, SUM(vflow_out) FROM Output_VFlow_Out WHERE scenario == '"
                + self.scenario
                + "' AND regions LIKE '"
                + self.region
                + "' GROUP BY sector, t_periods, tech"
            )
            self.output_vflow = cur.fetchall()
            self.output_vflow = [list(elem) for elem in self.output_vflow]
        elif type == 3:
            cur.execute(
                "SELECT sector, t_periods, emissions_comm, SUM(emissions) FROM Output_Emissions WHERE scenario == '"
                + self.scenario
                + "' AND regions LIKE '"
                + self.region
                + "' GROUP BY sector, t_periods, emissions_comm"
            )
            self.output_emissions = cur.fetchall()
            self.output_emissions = [list(elem) for elem in self.output_emissions]

        cur.execute("SELECT tech, tech_category FROM technologies")
        self.tech_categories = cur.fetchall()
        self.tech_categories = [
            [str(word) for word in tuple] for tuple in self.tech_categories
        ]
        con.close()

    def getSectors(self, type):
        """
        Based on the type of the plot being generated, returns a list of sectors available in the database
        """
        self.extractFromDatabase(type)
        sectors = set()

        data = None

        if type == 1:
            data = self.capacity_output
        elif type == 2:
            data = self.output_vflow
        elif type == 3:
            data = self.output_emissions

        for row in data:
            sectors.add(row[0])

        res = list(sectors)
        res.insert(0, "all")
        return res

    def processData(self, inputData, sector, super_categories=False):
        """
        Processes data for a particular sector to make it ready for plotting purposes
        """
        periods = set()
        techs = set()

        for row in inputData:
            row[0] = str(row[0])
            row[1] = int(row[1])
            row[2] = str(row[2])
            row[3] = float(row[3])

        tech_dict = dict(self.tech_categories)
        if super_categories:
            for row in inputData:
                row[2] = tech_dict.get(row[2], row[2])

        for row in inputData:
            if row[0] == sector or sector == "all":
                periods.add(row[1])  # Reminder: indexing starts at 0
                techs.add(row[2])

        periods = list(periods)
        techs = list(techs)
        periods.sort()

        output_values = dict()  # Each row in a dictionary is a list
        for tech in techs:
            if tech == "None" or tech == "":
                continue
            output_values[tech] = [0] * len(periods)  # this just creates a blank table
        for row in inputData:
            if row[2] == "None" or row[2] == "":
                continue
            if row[0] == sector or sector == "all":
                output_values[row[2]][periods.index(row[1])] += row[-1]

        output_values["periods"] = periods
        return output_values

    def handleOutputPath(self, plot_type, sector, super_categories, output_dir):
        outfile = plot_type + "_" + sector  # +'_'+str(int(time.time()*1000))+'.png'
        if super_categories:
            outfile += "_merged"
        outfile += ".png"
        outfile2 = os.path.join(self.folder_name, outfile)
        output_dir = os.path.join(output_dir, self.folder_name)
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        self.output_file_name = os.path.join(output_dir, outfile)

        self.output_file_name = self.output_file_name.replace(" ", "")
        return outfile2

    def generatePlotForCapacity(self, sector, super_categories=False, output_dir="."):
        """
        Generates Plot for Capacity of a given sector
        """

        outfile2 = self.handleOutputPath(
            "capacity", sector, super_categories, output_dir
        )
        if os.path.exists(self.output_file_name):
            print("not generating new capacity plot")
            return outfile2

        sectors = self.getSectors(1)

        if not (sector in sectors):
            return ""

        output_values = self.processData(self.capacity_output, sector, super_categories)

        if self.region == "%":
            title = "Capacity Plot for " + sector + " across all regions"
        else:
            title = "Capacity Plot for " + sector + " sector in region " + self.region

        self.makeStackedBarPlot(output_values, "Years", "Capacity ", "periods", title)

        return outfile2

    def generatePlotForOutputFlow(self, sector, super_categories=False, output_dir="."):
        """
        Generates Plot for Output Flow of a given sector
        """
        outfile2 = self.handleOutputPath("flow", sector, super_categories, output_dir)
        if os.path.exists(self.output_file_name):
            print("not generating new flow plot")
            return outfile2

        sectors = self.getSectors(2)
        if not (sector in sectors):
            return ""

        output_values = self.processData(self.output_vflow, sector, super_categories)

        if self.region == "%":
            title = "Output Flow Plot for " + sector + " across all regions"
        else:
            title = (
                "Output Flow Plot for " + sector + " sector in region " + self.region
            )

        self.makeStackedBarPlot(output_values, "Years", "Activity ", "periods", title)

        return outfile2

    def generatePlotForEmissions(self, sector, super_categories=False, output_dir="."):
        """
        Generates Plot for Emissions of a given sector
        """
        outfile2 = self.handleOutputPath(
            "emissions", sector, super_categories, output_dir
        )
        if os.path.exists(self.output_file_name):
            print("not generating new emissions plot")
            return outfile2

        sectors = self.getSectors(3)
        if not (sector in sectors):
            return ""

        output_values = self.processData(
            self.output_emissions, sector, super_categories
        )

        if self.region == "%":
            title = "Emissions Plot for " + sector + " across all regions"
        else:
            title = "Emissions Plot for " + sector + " sector in region " + self.region

        self.make_line_plot(output_values.copy(), "Emissions", title)

        return outfile2

    """
	--------------------------- Plot Generation related functions --------------------------------------
	"""

    def get_random_color(self, pastel_factor=0.5):
        return [
            (x + pastel_factor) / (1.0 + pastel_factor)
            for x in [random.uniform(0, 1.0) for i in [1, 2, 3]]
        ]

    def color_distance(self, c1, c2):
        return sum([abs(x[0] - x[1]) for x in zip(c1, c2)])

    def get_cmap(self, N):
        """Returns a function that maps each index in 0, 1, ... N-1 to a distinct
        RGB color."""
        color_norm = colors.Normalize(vmin=0, vmax=N - 1)
        # More colormaps: https://matplotlib.org/examples/color/colormaps_reference.html
        scalar_map = cmx.ScalarMappable(norm=color_norm, cmap="viridis")

        def map_index_to_rgb_color(index):
            return scalar_map.to_rgba(index)

        return map_index_to_rgb_color

    def generate_new_color(self, existing_colors, pastel_factor=0.5):
        max_distance = None
        best_color = None
        for i in range(0, 100):
            color = self.get_random_color(pastel_factor=pastel_factor)
            if not existing_colors:
                return color
            best_distance = min(
                [self.color_distance(color, c) for c in existing_colors]
            )
            if not max_distance or best_distance > max_distance:
                max_distance = best_distance
                best_color = color
        return best_color

    def makeStackedBarPlot(self, data, xlabel, ylabel, xvar, title):
        random.seed(10)

        handles = list()
        xaxis = data[xvar]
        data.pop("c", 0)
        data.pop(xvar, 0)
        stackedBars = data.keys()
        colorMapForBars = dict()
        colors = []
        plt.figure()

        cmap = self.get_cmap(len(stackedBars))
        for i in range(0, len(stackedBars)):
            # colors.append(self.generate_new_color(colors,pastel_factor = 0.9))
            # colorMapForBars[data.keys()[i]]=colors[i]
            colorMapForBars[list(data.keys())[i]] = cmap(i)

        width = min([xaxis[i + 1] - xaxis[i] for i in range(0, len(xaxis) - 1)]) / 2.0
        b = [0] * len(xaxis)

        # plt.figure()

        for bar in stackedBars:
            h = plt.bar(xaxis, data[bar], width, bottom=b, color=colorMapForBars[bar])
            handles.append(h)
            b = [b[j] + data[bar][j] for j in range(0, len(b))]

        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        # plt.xticks([width*0.5 + i for i in xaxis], [str(i) for i in xaxis])
        plt.xticks([i for i in xaxis], [str(i) for i in xaxis])
        plt.title(title)
        lgd = plt.legend(
            [h[0] for h in handles], stackedBars, bbox_to_anchor=(1.2, 1), fontsize=7.5
        )
        # plt.show()
        plt.savefig(
            self.output_file_name, bbox_extra_artists=(lgd,), bbox_inches="tight"
        )

    def make_line_plot(self, plot_var, label, title):
        handles = list()
        periods = plot_var["periods"]
        plot_var.pop("periods", 0)
        techs = plot_var.keys()
        random.seed(10)
        color_map = dict()
        colors = []
        width = 1.5
        plt.figure()

        cmap = self.get_cmap(len(techs))
        for i in range(0, len(techs)):
            # colors.append(self.generate_new_color(colors,pastel_factor = 0.9))
            # color_map[plot_var.keys()[i]]=colors[i]
            color_map[plot_var.keys()[i]] = cmap(i)

        b = [0] * len(periods)
        for tech in techs:
            h = plt.plot(
                periods,
                plot_var[tech],
                color=color_map[tech],
                linestyle="--",
                marker="o",
            )
            handles.append(h)

        plt.xlabel("Years")
        plt.ylabel(label)
        # plt.xticks([i + width*0.5 for i in periods], [str(i) for i in periods])
        plt.xticks(periods)
        plt.title(title)
        lgd = plt.legend(
            [h[0] for h in handles], techs, bbox_to_anchor=(1.2, 1), fontsize=7.5
        )
        # plt.show()
        plt.savefig(
            self.output_file_name, bbox_extra_artists=(lgd,), bbox_inches="tight"
        )


# Function used for command line purposes. Parses arguments and then calls relevent functions.
def GeneratePlot(args):
    parser = argparse.ArgumentParser(description="Generate Output Plot")
    parser.add_argument(
        "-i",
        "--input",
        action="store",
        dest="input",
        help="Input Database Filename <path>",
        required=True,
    )
    parser.add_argument(
        "-r",
        "--region",
        action="store",
        dest="region",
        help="Region name, input 'global' if global results are desired",
        required=True,
    )
    parser.add_argument(
        "-s",
        "--scenario",
        action="store",
        dest="scenario",
        help="Model run scenario name",
        required=True,
    )
    parser.add_argument(
        "-p",
        "--plot-type",
        action="store",
        dest="type",
        help="Type of Plot to be generated",
        choices=["capacity", "flow", "emissions"],
        required=True,
    )
    parser.add_argument(
        "-c",
        "--sector",
        action="store",
        dest="sector",
        help="Sector for which plot to be generated",
        required=True,
    )
    parser.add_argument(
        "-o",
        "--output",
        action="store",
        dest="output_dir",
        help="Output plot location",
        default="./",
    )
    parser.add_argument(
        "--super",
        action="store_true",
        dest="super_categories",
        help="Merge Technologies or not",
        default=False,
    )

    options = parser.parse_args(args)

    result = OutputPlotGenerator(
        options.input, options.region, options.scenario, options.super_categories
    )
    error = ""
    if options.type == "capacity":
        error = result.generatePlotForCapacity(
            options.sector, options.super_categories, options.output_dir
        )
    elif options.type == "flow":
        error = result.generatePlotForOutputFlow(
            options.sector, options.super_categories, options.output_dir
        )
    elif options.type == "emissions":
        error = result.generatePlotForEmissions(
            options.sector, options.super_categories, options.output_dir
        )

    if error == "":
        print("Error: The sector doesn't exist for the selected plot type and database")
    else:
        print(
            "Done. Look for output plot images in directory:"
            + os.path.join(options.output_dir, error)
        )


if __name__ == "__main__":
    GeneratePlot(sys.argv[1:])
