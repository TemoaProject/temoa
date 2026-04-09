import argparse
import os
from subprocess import call
from typing import Any, TextIO

from temoa.utilities.graphviz_formats import (
    commodity_dot_fmt,
    quick_run_dot_fmt,
    results_dot_fmt,
    tech_results_dot_fmt,
)
from temoa.utilities.graphviz_util import (
    create_text_edges,
    create_text_nodes,
    get_color_config,
)

from .database_util import DatabaseUtil


def process_input(args: list[str]) -> dict[str, Any]:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Generate Output Plot')
    parser.add_argument(
        '-i',
        '--input',
        action='store',
        dest='ifile',
        help='Input Database Filename <path>',
        required=True,
    )
    parser.add_argument(
        '-f',
        '--format',
        action='store',
        dest='image_format',
        help='Graphviz output format (Default: svg)',
        default='svg',
    )
    parser.add_argument(
        '-c',
        '--show_capacity',
        action='store_true',
        dest='show_capacity',
        help='Whether capacity shows up in subgraphs (Default: not shown)',
        default=False,
    )
    parser.add_argument(
        '-v',
        '--splinevar',
        action='store_true',
        dest='splinevar',
        help='Whether subgraph edges to be straight or curved (Default: Straight)',
        default=False,
    )
    parser.add_argument(
        '-t',
        '--graph_type',
        action='store',
        dest='graph_type',
        help='Type of subgraph (Default: separate_vintages)',
        choices=['separate_vintages', 'explicit_vintages'],
        default='separate_vintages',
    )
    parser.add_argument(
        '-g',
        '--gray',
        action='store_true',
        dest='grey_flag',
        help='If specified, generates graph in graycale',
        default=False,
    )
    parser.add_argument(
        '-n',
        '--name',
        action='store',
        dest='quick_name',
        help='Specify the extension you wish to give your quick run',
    )
    parser.add_argument(
        '-o',
        '--output',
        action='store',
        dest='res_dir',
        help='Optional output file path (to dump the images folder)',
        default='./',
    )

    group1 = parser.add_mutually_exclusive_group()
    group1.add_argument(
        '-b',
        '--technology',
        action='store',
        dest='inp_technology',
        help='Technology for which graph to be generated',
    )
    group1.add_argument(
        '-a',
        '--commodity',
        action='store',
        dest='inp_commodity',
        help='Commodity for which graph to be generated',
    )

    parser.add_argument(
        '-s',
        '--scenario',
        action='store',
        dest='scenario_name',
        help='Model run scenario name',
        default=None,
    )
    parser.add_argument(
        '-y',
        '--year',
        action='store',
        dest='period',
        type=int,
        help='The period for which the graph is to be generated (Used only for output plots)',
    )
    parser.add_argument(
        '-r',
        '--region',
        action='store',
        dest='region',
        help='The region for which the graph is to be generated',
        default=None,
    )

    options = parser.parse_args(args)

    if (options.scenario_name is not None) ^ (options.period is not None):
        parser.print_help()
        raise ValueError('Scenario and input year must both be present or not present together')

    return vars(options)


class GraphvizDiagramGenerator:
    """Generates Graphviz diagrams for Temoa models."""

    db_file: str
    q_name: str
    scenario: str | None
    region: str | None
    out_dir: str
    folder: dict[str, str]
    verbose: int
    colors: dict[str, Any]
    db_util: DatabaseUtil
    logger: TextIO
    grey_flag: bool

    def __init__(
        self,
        db_file: str,
        scenario: str | None = None,
        region: str | None = None,
        out_dir: str = '.',
        verbose: int = 1,
    ) -> None:
        """Initialize the GraphvizDiagramGenerator."""
        self.db_file = db_file
        self.q_name = os.path.splitext(os.path.basename(self.db_file))[0]
        self.scenario = scenario
        self.region = region
        self.out_dir = out_dir
        self.folder = {'results': 'whole_system', 'tech': 'processes', 'comm': 'commodities'}
        self.verbose = verbose
        self.colors = {}
        self.grey_flag = False

    def connect(self) -> None:
        """Connect to the database and set up output directories."""
        self.db_util = DatabaseUtil(self.db_file, self.scenario)
        self.logger = open(os.path.join(self.out_dir, 'graphviz.log'), 'w')
        self.set_graphic_options(False, False)
        self.__log__('--------------------------------------')
        self.__log__('GraphvizDiagramGenerator: connected')
        if self.scenario:
            out_dir = f'{self.q_name}_{self.scenario}_graphviz'
        else:
            out_dir = f'{self.q_name}_input_graphviz'

        self.out_dir = os.path.join(self.out_dir, out_dir)
        if not os.path.exists(self.out_dir):
            os.mkdir(self.out_dir)

    def close(self) -> None:
        """Disconnect from the database and close the logger."""
        self.db_util.close()
        self.__log__('GraphvizDiagramGenerator: disconnected')
        self.__log__('--------------------------------------')
        self.logger.close()

    def __log__(self, msg: str) -> None:
        """Log a message to the console and a log file."""
        if self.verbose == 1:
            print(msg)
        self.logger.write(msg + '\n')

    def __generate_graph__(
        self, dot_format: str, dot_args: dict[str, Any], output_name: str, output_format: str
    ) -> None:
        """Generate a graph from a DOT format string."""
        dot_args.update(self.colors)
        with open(output_name + '.dot', 'w') as f:
            f.write(dot_format.format(**dot_args))
        cmd = (
            'dot',
            f'-T{output_format}',
            f'-o{output_name}.{output_format}',
            f'{output_name}.dot',
        )
        call(cmd)

    def set_graphic_options(
        self, grey_flag: bool | None = None, splinevar: bool | None = None
    ) -> None:
        """Set graphic options for the diagrams."""
        if grey_flag is not None:
            self.grey_flag = grey_flag
            self.colors.update(get_color_config(grey_flag=self.grey_flag))
        if splinevar is not None:
            self.colors['splinevar'] = 'spline' if splinevar else 'line'
        self.__log__(
            f'setGraphicOption: updated greyFlag = {self.grey_flag} '
            f'and splinevar = {self.colors.get("splinevar", "line")}'
        )

    def create_main_results_diagram(
        self, period: int, region: str | None, output_format: str = 'svg'
    ) -> tuple[str, str]:
        """Create the main results diagram for a specific period."""
        self.__log__(f'CreateMainResultsDiagram: started with period = {period}')

        results_dir = os.path.join(self.out_dir, self.folder['results'])
        if not os.path.exists(results_dir):
            os.makedirs(results_dir)

        output_name = os.path.join(self.folder['results'], f'results{period}')
        if self.region:
            output_name += f'_{self.region}'
        output_name = os.path.join(self.out_dir, output_name)
        if self.grey_flag:
            output_name += '.grey'

        tech_all = self.db_util.get_technologies_for_flags(flags=['r', 'p', 'pb', 'ps'])
        commodity_carrier = self.db_util.get_commodities_for_flags(flags=['d', 'p'])
        commodity_emissions = self.db_util.get_commodities_for_flags(flags=['e'])
        efficiency_input = self.db_util.get_commodities_by_technology(region, comm_type='input')
        efficiency_output = self.db_util.get_commodities_by_technology(region, comm_type='output')
        v_cap2 = self.db_util.get_capacity_for_tech_and_period(period=period, region=region)
        ei_2 = self.db_util.get_output_flow_for_period(
            period=period, region=region, comm_type='input'
        )
        eo_2 = self.db_util.get_output_flow_for_period(
            period=period, region=region, comm_type='output'
        )
        emio_2 = self.db_util.get_emissions_activity_for_period(period=period, region=region)

        self.__log__('CreateMainResultsDiagram: database fetched successfully')

        tech_attr_fmt = (
            'label="%s\\nCapacity: %.2f", href="#", '
            "onclick=\"loadNextGraphvizGraph('results', '%s', '%s')\""
        )
        commodity_fmt = "href=\"#\", onclick=\"loadNextGraphvizGraph('results', '%s', '%s')\""
        flow_fmt = 'label="%.2f"'
        epsilon = 0.005

        etechs: set[tuple[str, str]] = set()
        dtechs: set[tuple[str, str]] = set()
        ecarriers: set[tuple[str, str]] = set()
        xnodes: set[tuple[str, str]] = set()
        eemissions: set[tuple[str, str]] = set()
        eflowsi: set[tuple[str, str, str]] = set()
        eflowso: set[tuple[str, str, str]] = set()
        dflows: set[tuple[str, str, str]] = set()
        usedc, usede = set(), set()  # used carriers, used emissions

        v_cap2.index = v_cap2.tech
        for tech in set(tech_all) - set(v_cap2.tech):
            dtechs.add((tech, ''))

        for i in range(len(v_cap2)):
            row = v_cap2.iloc[i]
            etechs.add(
                (row['tech'], tech_attr_fmt % (row['tech'], row['capacity'], row['tech'], period))
            )

        udflows: set[tuple[str, str]] = set()
        for i in range(len(ei_2)):
            row = ei_2.iloc[i]
            if row['input_comm'] != 'ethos':
                eflowsi.add((row['input_comm'], row['tech'], flow_fmt % row['flow']))
                ecarriers.add((row['input_comm'], commodity_fmt % (row['input_comm'], period)))
                usedc.add(row['input_comm'])
            else:
                tech = row['tech']
                cap = v_cap2.loc[row['tech']].capacity if tech in v_cap2.tech else 99999
                xnodes.add((row['tech'], tech_attr_fmt % (row['tech'], cap, row['tech'], period)))
            udflows.add((row['input_comm'], row['tech']))

        for row in set(efficiency_input) - udflows:
            if row[0] != 'ethos':
                dflows.add((row[0], row[1], ''))
            else:
                xnodes.add((row[1], ''))

        udflows = set()
        for i in range(len(eo_2)):
            row = eo_2.iloc[i]
            eflowso.add((row['tech'], row['output_comm'], flow_fmt % row['flow']))
            ecarriers.add((row['output_comm'], commodity_fmt % (row['output_comm'], period)))
            usedc.add(row['output_comm'])
            udflows.add((row['tech'], row['output_comm']))

        for row in set(efficiency_output) - udflows:
            dflows.add((row[0], row[1], ''))

        for i in range(len(emio_2)):
            row = emio_2.iloc[i]
            if row['emis_activity'] >= epsilon:
                eflowso.add((row['tech'], row['emis_comm'], flow_fmt % row['emis_activity']))
                eemissions.add((row['emis_comm'], ''))
                usede.add(row['emis_comm'])

        dcarriers = {(cc, '') for cc in commodity_carrier if cc not in usedc and cc != 'ethos'}
        demissions = {(ee, '') for ee in commodity_emissions if ee not in usede}

        self.__log__('CreateMainResultsDiagram: creating diagrams')
        args = {
            'period': period,
            'splinevar': self.colors['splinevar'],
            'dtechs': create_text_nodes(dtechs, indent=2),
            'etechs': create_text_nodes(etechs, indent=2),
            'xnodes': create_text_nodes(xnodes, indent=2),
            'dcarriers': create_text_nodes(dcarriers, indent=2),
            'ecarriers': create_text_nodes(ecarriers, indent=2),
            'demissions': create_text_nodes(demissions, indent=2),
            'eemissions': create_text_nodes(eemissions, indent=2),
            'dflows': create_text_edges(dflows, indent=2),
            'eflowsi': create_text_edges(eflowsi, indent=3),
            'eflowso': create_text_edges(eflowso, indent=3),
        }

        output_path = output_name + '.' + output_format
        self.__generate_graph__(results_dot_fmt, args, output_name, output_format)
        self.__log__('CreateMainResultsDiagram: graph generated, returning')
        return self.out_dir, output_path

    def create_tech_results_diagrams(
        self, period: int, region: str | None, tech: str, output_format: str = 'svg'
    ) -> tuple[str, str]:
        """Create technology-specific results diagrams."""
        self.__log__(f'CreateTechResultsDiagrams: started with period = {period} and tech = {tech}')

        tech_dir = os.path.join(self.out_dir, self.folder['tech'])
        if not os.path.exists(tech_dir):
            os.makedirs(tech_dir)

        output_name = os.path.join(self.folder['tech'], f'results_{tech}_{period}')
        if self.region:
            output_name += f'_{self.region}'
        output_name = os.path.join(self.out_dir, output_name)
        if self.grey_flag:
            output_name += '.grey'

        enode_attr_fmt = "href=\"#\", onclick=\"loadNextGraphvizGraph('results', '%s', '%s')\""
        vnode_attr_fmt = (
            "href=\"#\", onclick=\"loadNextGraphvizGraph('%s', '%s', '%s')\", "
            'label="%s\\nCap: %.2f"'
        )

        total_cap = self.db_util.get_capacity_for_tech_and_period(tech, period, region)
        flows = self.db_util.get_commodity_wise_input_and_output_flow(tech, period, region)
        self.__log__('CreateTechResultsDiagrams: database fetched successfully')

        enodes: set[tuple[str, str]] = set()
        vnodes: set[tuple[str, str]] = set()
        iedges: set[tuple[str, str, str]] = set()
        oedges: set[tuple[str, str, str]] = set()

        for i in range(len(flows)):
            row = flows.iloc[i]
            vnode = str(row['vintage'])
            vnodes.add(
                (
                    vnode,
                    vnode_attr_fmt
                    % (tech, period, row['vintage'], row['vintage'], row['capacity']),
                )
            )

            if row['input_comm'] != 'ethos':
                enodes.add((row['input_comm'], enode_attr_fmt % (row['input_comm'], period)))
                iedges.add((row['input_comm'], vnode, 'label="{:.2f}"'.format(row['flow_in'])))
            enodes.add((row['output_comm'], enode_attr_fmt % (row['output_comm'], period)))
            oedges.add((vnode, row['output_comm'], 'label="{:.2f}"'.format(row['flow_out'])))

        output_path = output_name + '.' + output_format
        if vnodes:
            self.__log__('CreateTechResultsDiagrams: creating diagrams')
            args: dict[str, Any] = {
                'cluster_vintage_url': '#',
                'total_cap': total_cap,
                'inp_technology': tech,
                'period': period,
                'vnodes': create_text_nodes(vnodes, indent=2),
                'enodes': create_text_nodes(enodes, indent=2),
                'iedges': create_text_edges(iedges, indent=2),
                'oedges': create_text_edges(oedges, indent=2),
            }
            self.__generate_graph__(tech_results_dot_fmt, args, output_name, output_format)
        else:
            self.__log__('CreateTechResultsDiagrams: nothing to create')

        self.__log__('CreateTechResultsDiagrams: graph generated, returning')
        return self.out_dir, output_path

    def create_commodity_partial_results(
        self, period: int, region: str | None, comm: str, output_format: str = 'svg'
    ) -> tuple[str, str]:
        """Create commodity-specific partial results diagrams."""
        self.__log__(
            f'CreateCommodityPartialResults: started with period = {period} and comm = {comm}'
        )

        comm_dir = os.path.join(self.out_dir, self.folder['comm'])
        if not os.path.exists(comm_dir):
            os.makedirs(comm_dir)

        output_name = os.path.join(self.folder['comm'], f'rc_{comm}_{period}')
        if self.region:
            output_name += f'_{self.region}'
        output_name = os.path.join(self.out_dir, output_name)
        if self.grey_flag:
            output_name += '.grey'

        input_total = set(
            self.db_util.get_existing_technologies_for_commodity(comm, region, 'output')['tech']
        )
        output_total = set(
            self.db_util.get_existing_technologies_for_commodity(comm, region, 'input')['tech']
        )
        flow_in = self.db_util.get_output_flow_for_period(period, region, 'input', comm)
        otechs = set(flow_in['tech'])
        flow_out = self.db_util.get_output_flow_for_period(period, region, 'output', comm)
        itechs = set(flow_out['tech'])
        self.__log__('CreateCommodityPartialResults: database fetched successfully')

        node_attr_fmt = "href=\"#\", onclick=\"loadNextGraphvizGraph('results', '%s', '%s')\""
        rc_node_fmt = 'color="%s", href="%s", shape="circle", fillcolor="%s", fontcolor="black"'

        enodes: set[tuple[str, str]] = set()
        dnodes: set[tuple[str, str]] = set()
        eedges: set[tuple[str, str, str]] = set()
        dedges: set[tuple[str, str, str]] = set()

        rcnode = (
            (comm, rc_node_fmt % (self.colors['commodity_color'], '#', self.colors['fill_color'])),
        )

        for i in range(len(flow_in)):
            t = flow_in.iloc[i]['tech']
            f = flow_in.iloc[i]['flow']
            enodes.add((t, node_attr_fmt % (t, period)))
            eedges.add((comm, t, f'label="{f:.2f}"'))
        for t in output_total - otechs:
            dnodes.add((t, ''))
            dedges.add((comm, t, ''))
        for i in range(len(flow_out)):
            t = flow_out.iloc[i]['tech']
            f = flow_out.iloc[i]['flow']
            enodes.add((t, node_attr_fmt % (t, period)))
            eedges.add((t, comm, f'label="{f:.2f}"'))
        for t in input_total - itechs:
            dnodes.add((t, ''))
            dedges.add((t, comm, ''))

        self.__log__('CreateCommodityPartialResults: creating diagrams')
        args = {
            'inp_commodity': comm,
            'period': period,
            'resource_node': create_text_nodes(rcnode),
            'used_nodes': create_text_nodes(enodes, indent=2),
            'unused_nodes': create_text_nodes(dnodes, indent=2),
            'used_edges': create_text_edges(eedges, indent=2),
            'unused_edges': create_text_edges(dedges, indent=2),
        }
        output_path = output_name + '.' + output_format
        self.__generate_graph__(commodity_dot_fmt, args, output_name, output_format)
        self.__log__('CreateCommodityPartialResults: graph generated, returning')
        return self.out_dir, output_path

    def create_complete_input_graph(
        self,
        region: str | None,
        inp_tech: str | None = None,
        inp_comm: str | None = None,
        output_format: str = 'svg',
    ) -> tuple[str, str]:
        """Generate the complete input graph."""
        self.__log__(
            f'createCompleteInputGraph: started with inp_tech = {inp_tech} '
            f'and inp_comm = {inp_comm}'
        )
        output_name = self.q_name

        if inp_tech:
            output_name += f'_{inp_tech}'
            tech_dir = os.path.join(self.out_dir, self.folder['tech'])
            if not os.path.exists(tech_dir):
                os.makedirs(tech_dir)
            output_name = os.path.join(self.folder['tech'], output_name)
        elif inp_comm:
            output_name += f'_{inp_comm}'
            comm_dir = os.path.join(self.out_dir, self.folder['comm'])
            if not os.path.exists(comm_dir):
                os.makedirs(comm_dir)
            output_name = os.path.join(self.folder['comm'], output_name)
        else:
            results_dir = os.path.join(self.out_dir, self.folder['results'])
            if not os.path.exists(results_dir):
                os.makedirs(results_dir)
            output_name = os.path.join(self.folder['results'], output_name)

        if self.region:
            output_name += f'_{self.region}'

        output_name = os.path.join(self.out_dir, output_name)
        if self.grey_flag:
            output_name += '.grey'

        nodes, tech, ltech, to_tech, from_tech = set(), set(), set(), set(), set()

        res = (
            self.db_util.get_commodities_and_tech(inp_comm, inp_tech, region)
            if DatabaseUtil.is_database_file(self.db_file)
            else self.db_util.read_from_dat_file(inp_comm, inp_tech)
        )

        self.__log__('createCompleteInputGraph: database fetched successfully')
        for i in range(len(res)):
            row = res.iloc[i]
            if row['input_comm'] != 'ethos':
                nodes.add(row['input_comm'])
            else:
                ltech.add(row['tech'])
            nodes.add(row['output_comm'])
            tech.add(row['tech'])

            if row['input_comm'] != 'ethos':
                to_tech.add(f'"{row["input_comm"]}"\t->\t"{row["tech"]}"')
            from_tech.add(f'"{row["tech"]}"\t->\t"{row["output_comm"]}"')

        self.__log__('createCompleteInputGraph: creating diagrams')

        args = {
            'enodes': ''.join(f'"{x}";\n\t\t' for x in nodes),
            'tnodes': ''.join(f'"{x}";\n\t\t' for x in tech),
            'iedges': ''.join(f'{x};\n\t\t' for x in to_tech),
            'oedges': ''.join(f'{x};\n\t\t' for x in from_tech),
            'snodes': ';'.join(f'"{x}"' for x in ltech),
        }
        output_path = output_name + '.' + output_format
        self.__generate_graph__(quick_run_dot_fmt, args, output_name, output_format)
        self.__log__('createCompleteInputGraph: graph generated, returning')
        return self.out_dir, output_path
