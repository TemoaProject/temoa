import os
import sys
from subprocess import call

from database_util import DatabaseUtil
from graphviz_formats import (
    commodity_dot_fmt,
    quick_run_dot_fmt,
    results_dot_fmt,
    tech_results_dot_fmt,
)
from graphviz_util import create_text_edges, create_text_nodes, get_color_config, process_input


class GraphvizDiagramGenerator:
    def __init__(self, db_file, scenario=None, region=None, out_dir='.', verbose=1):
        self.dbFile = db_file
        self.qName = os.path.splitext(os.path.basename(self.dbFile))[0]
        self.scenario = scenario
        self.region = region
        self.outDir = out_dir
        self.folder = {'results': 'whole_system', 'tech': 'processes', 'comm': 'commodities'}
        self.verbose = verbose
        self.colors = {}

    def connect(self):
        self.dbUtil = DatabaseUtil(self.dbFile, self.scenario)
        self.logger = open(os.path.join(self.outDir, 'graphviz.log'), 'w')
        self.set_graphic_options(False, False)
        self.__log__('--------------------------------------')
        self.__log__('GraphvizDiagramGenerator: connected')
        if self.scenario:
            out_dir = self.qName + '_' + self.scenario + '_graphviz'
        else:
            out_dir = self.qName + '_input_graphviz'

        self.outDir = os.path.join(self.outDir, out_dir)
        if not os.path.exists(self.outDir):
            os.mkdir(self.outDir)
        # os.chdir(self.outDir)

    def close(self):
        self.dbUtil.close()
        self.__log__('GraphvizDiagramGenerator: disconnected')
        self.__log__('--------------------------------------')
        self.logger.close()
        # os.chdir('..')

    def __log__(self, msg):
        if self.verbose == 1:
            print(msg)
        self.logger.write(msg + '\n')

    def __generate_graph__(self, dot_format, dot_args, output_name, output_format):
        dot_args.update(self.colors)
        with open(output_name + '.dot', 'w') as f:
            f.write(dot_format % dot_args)
        cmd = (
            'dot',
            '-T' + output_format,
            '-o' + output_name + '.' + output_format,
            output_name + '.dot',
        )
        call(cmd)

    def set_graphic_options(self, grey_flag=None, splinevar=None):
        if grey_flag is not None:
            self.greyFlag = grey_flag
            self.colors.update(get_color_config(self.greyFlag))
        if splinevar is not None:
            self.colors['splinevar'] = splinevar
        self.__log__(
            'setGraphicOption: updated greyFlag = '
            + str(self.greyFlag)
            + ' and splinevar = '
            + str(self.colors['splinevar'])
        )

    def create_main_results_diagram(self, period, region, output_format='svg'):
        self.__log__('CreateMainResultsDiagram: started with period = ' + str(period))

        if not os.path.exists(os.path.join(self.outDir, self.folder['results'])):
            os.makedirs(os.path.join(self.outDir, self.folder['results']))

        output_name = os.path.join(self.folder['results'], 'results%s' % period)
        if self.region:
            output_name += '_' + self.region
        output_name = os.path.join(self.outDir, output_name)
        if self.greyFlag:
            output_name += '.grey'
        # if (os.path.exists(outputName + '.' + outputFormat)):
        # self.__log__('CreateMainResultsDiagram: graph already exists at path, returning')
        # return self.outDir, outputName + '.' + outputFormat

        tech_all = self.dbUtil.get_technologies_for_flags(flags=['r', 'p', 'pb', 'ps'])

        commodity_carrier = self.dbUtil.get_commodities_for_flags(flags=['d', 'p'])
        commodity_emissions = self.dbUtil.get_commodities_for_flags(flags=['e'])

        efficiency_input = self.dbUtil.get_commodities_by_technology(region, comm_type='input')
        efficiency_output = self.dbUtil.get_commodities_by_technology(region, comm_type='output')

        v_cap2 = self.dbUtil.get_capacity_for_tech_and_period(period=period, region=region)

        ei_2 = self.dbUtil.get_output_flow_for_period(
            period=period, region=region, comm_type='input'
        )
        eo_2 = self.dbUtil.get_output_flow_for_period(
            period=period, region=region, comm_type='output'
        )

        emio_2 = self.dbUtil.get_emissions_activity_for_period(period=period, region=region)

        self.__log__('CreateMainResultsDiagram: database fetched successfully')

        tech_attr_fmt = 'label="%s\\nCapacity: %.2f", href="#", onclick="loadNextGraphvizGraph(\'results\', \'%s\', \'%s\')"'
        # tech_attr_fmt = 'label="%%s\\nCapacity: %%.2f", href="results_%%s_%%s.%s"'
        # tech_attr_fmt %= outputFormat
        # commodity_fmt = 'href="../commodities/rc_%%s_%%s.%s"' % outputFormat
        commodity_fmt = "href=\"#\", onclick=\"loadNextGraphvizGraph('results', '%s', '%s')\""
        flow_fmt = 'label="%.2f"'

        epsilon = 0.005

        etechs, dtechs, ecarriers, xnodes = set(), set(), set(), set()
        eemissions = set()
        eflowsi, eflowso, dflows = set(), set(), set()  # edges
        usedc, usede = set(), set()  # used carriers, used emissions

        v_cap2.index = v_cap2.tech
        for tech in set(tech_all) - set(v_cap2.tech):
            dtechs.add((tech, None))

        for i in range(len(v_cap2)):
            row = v_cap2.iloc[i]
            etechs.add(
                (row['tech'], tech_attr_fmt % (row['tech'], row['capacity'], row['tech'], period))
            )
            # etechs.add( (row['tech'], tech_attr_fmt % (row['tech'], row['capacity'], row['tech'], period)) )

        udflows = set()
        for i in range(len(ei_2)):
            row = ei_2.iloc[i]
            if row['input_comm'] != 'ethos':
                eflowsi.add((row['input_comm'], row['tech'], flow_fmt % row['flow']))
                ecarriers.add((row['input_comm'], commodity_fmt % (row['input_comm'], period)))
                usedc.add(row['input_comm'])
            else:
                # check to see if this tech is in the unlim_cap set
                tech = row['tech']
                if tech not in v_cap2.tech:
                    cap = 99999
                else:
                    cap = v_cap2.loc[row['tech']].capacity
                xnodes.add((row['tech'], tech_attr_fmt % (row['tech'], cap, row['tech'], period)))
            udflows.add((row['input_comm'], row['tech']))

        for row in set(efficiency_input) - udflows:
            if row[0] != 'ethos':
                dflows.add((row[0], row[1], None))
            else:
                xnodes.add((row[1], None))

        udflows = set()
        for i in range(len(eo_2)):
            row = eo_2.iloc[i]
            eflowso.add((row['tech'], row['output_comm'], flow_fmt % row['flow']))
            ecarriers.add((row['output_comm'], commodity_fmt % (row['output_comm'], period)))
            usedc.add(row['output_comm'])
            udflows.add((row['tech'], row['output_comm']))

        for row in set(efficiency_output) - udflows:
            dflows.add((row[0], row[1], None))

        for i in range(len(emio_2)):
            row = emio_2.iloc[i]
            if row['emis_activity'] >= epsilon:
                eflowso.add((row['tech'], row['emis_comm'], flow_fmt % row['emis_activity']))
                eemissions.add((row['emis_comm'], None))
                usede.add(row['emis_comm'])

        dcarriers = set()
        demissions = set()
        for cc in commodity_carrier:
            if cc not in usedc and cc != 'ethos':
                dcarriers.add((cc, None))
        for ee in commodity_emissions:
            if ee not in usede:
                demissions.add((ee, None))

        self.__log__('CreateMainResultsDiagram: creating diagrams')
        args = dict(
            period=period,
            splinevar=self.colors['splinevar'],
            dtechs=create_text_nodes(dtechs, indent=2),
            etechs=create_text_nodes(etechs, indent=2),
            xnodes=create_text_nodes(xnodes, indent=2),
            dcarriers=create_text_nodes(dcarriers, indent=2),
            ecarriers=create_text_nodes(ecarriers, indent=2),
            demissions=create_text_nodes(demissions, indent=2),
            eemissions=create_text_nodes(eemissions, indent=2),
            dflows=create_text_edges(dflows, indent=2),
            eflowsi=create_text_edges(eflowsi, indent=3),
            eflowso=create_text_edges(eflowso, indent=3),
        )

        self.__generate_graph__(results_dot_fmt, args, output_name, output_format)
        self.__log__('CreateMainResultsDiagram: graph generated, returning')
        return self.outDir, output_name + '.' + output_format

    # Needs some small fixing - cases where no input but output is there. # Check sample graphs
    def create_tech_results_diagrams(
        self, period, region, tech, output_format='svg'
    ):  # tech results
        self.__log__(
            'CreateTechResultsDiagrams: started with period = '
            + str(period)
            + ' and tech = '
            + str(tech)
        )

        if not os.path.exists(os.path.join(self.outDir, self.folder['tech'])):
            os.makedirs(os.path.join(self.outDir, self.folder['tech']))

        output_name = os.path.join(self.folder['tech'], f'results_{tech}_{period}')
        if self.region:
            output_name += '_' + self.region
        output_name = os.path.join(self.outDir, output_name)
        if self.greyFlag:
            output_name += '.grey'
        # if (os.path.exists(outputName + '.' + outputFormat)):
        # self.__log__('CreateTechResultsDiagrams: graph already exists at path, returning')
        # return self.outDir, outputName + '.' + outputFormat

        # enode_attr_fmt = 'href="../commodities/rc_%%s_%%s.%s"' % outputFormat
        # vnode_attr_fmt = 'href="results_%%s_p%%sv%%s_segments.%s", ' % outputFormat
        # vnode_attr_fmt += 'label="%s\\nCap: %.2f"'
        enode_attr_fmt = "href=\"#\", onclick=\"loadNextGraphvizGraph('results', '%s', '%s')\""
        vnode_attr_fmt = "href=\"#\", onclick=\"loadNextGraphvizGraph('%s', '%s', '%s')\""
        vnode_attr_fmt += 'label="%s\\nCap: %.2f"'

        total_cap = self.dbUtil.get_capacity_for_tech_and_period(tech, period, region)
        flows = self.dbUtil.get_commodity_wise_input_and_output_flow(tech, period, region)

        self.__log__('CreateTechResultsDiagrams: database fetched successfully')

        enodes, vnodes, iedges, oedges = set(), set(), set(), set()
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
                iedges.add((row['input_comm'], vnode, 'label="%.2f"' % row['flow_in']))
            enodes.add((row['output_comm'], enode_attr_fmt % (row['output_comm'], period)))
            oedges.add((vnode, row['output_comm'], 'label="%.2f"' % row['flow_out']))

        # cluster_vintage_url = "results%s.%s" % (period, outputFormat)
        cluster_vintage_url = '#'

        if vnodes:
            self.__log__('CreateTechResultsDiagrams: creating diagrams')
            args = dict(
                cluster_vintage_url=cluster_vintage_url,
                total_cap=total_cap,
                inp_technology=tech,
                period=period,
                vnodes=create_text_nodes(vnodes, indent=2),
                enodes=create_text_nodes(enodes, indent=2),
                iedges=create_text_edges(iedges, indent=2),
                oedges=create_text_edges(oedges, indent=2),
            )
            self.__generate_graph__(tech_results_dot_fmt, args, output_name, output_format)
        else:
            self.__log__('CreateTechResultsDiagrams: nothing to create')

        self.__log__('CreateTechResultsDiagrams: graph generated, returning')
        return self.outDir, output_name + '.' + output_format

    def create_commodity_partial_results(self, period, region, comm, output_format='svg'):
        self.__log__(
            'CreateCommodityPartialResults: started with period = '
            + str(period)
            + ' and comm = '
            + str(comm)
        )

        if not os.path.exists(os.path.join(self.outDir, self.folder['comm'])):
            os.makedirs(os.path.join(self.outDir, self.folder['comm']))

        output_name = os.path.join(self.folder['comm'], f'rc_{comm}_{period}')
        if self.region:
            output_name += '_' + self.region
        output_name = os.path.join(self.outDir, output_name)
        if self.greyFlag:
            output_name += '.grey'
        # if (os.path.exists(outputName + '.' + outputFormat)):
        # self.__log__('CreateCommodityPartialResults: graph already exists at path, returning')
        # return self.outDir, outputName + '.' + outputFormat

        input_total = set(
            self.dbUtil.get_existing_technologies_for_commodity(comm, region, 'output')['tech']
        )
        output_total = set(
            self.dbUtil.get_existing_technologies_for_commodity(comm, region, 'input')['tech']
        )

        flow_in = self.dbUtil.get_output_flow_for_period(period, region, 'input', comm)
        otechs = set(flow_in['tech'])

        flow_out = self.dbUtil.get_output_flow_for_period(period, region, 'output', comm)
        itechs = set(flow_out['tech'])

        self.__log__('CreateCommodityPartialResults: database fetched successfully')

        # period_results_url_fmt = '../results/results%%s.%s' % outputFormat
        # node_attr_fmt = 'href="../results/results_%%s_%%s.%s"' % outputFormat
        # rc_node_fmt = 'color="%s", href="%s", shape="circle", fillcolor="%s", fontcolor="black"'

        node_attr_fmt = "href=\"#\", onclick=\"loadNextGraphvizGraph('results', '%s', '%s')\""
        rc_node_fmt = 'color="%s", href="%s", shape="circle", fillcolor="%s", fontcolor="black"'

        # url = period_results_url_fmt % period
        url = '#'
        enodes, dnodes, eedges, dedges = set(), set(), set(), set()

        rcnode = (
            (comm, rc_node_fmt % (self.colors['commodity_color'], url, self.colors['fill_color'])),
        )

        for i in range(len(flow_in)):
            t = flow_in.iloc[i]['tech']
            f = flow_in.iloc[i]['flow']
            enodes.add((t, node_attr_fmt % (t, period)))
            eedges.add((comm, t, 'label="%.2f"' % f))
        for t in output_total - otechs:
            dnodes.add((t, None))
            dedges.add((comm, t, None))
        for i in range(len(flow_out)):
            t = flow_out.iloc[i]['tech']
            f = flow_out.iloc[i]['flow']
            enodes.add((t, node_attr_fmt % (t, period)))
            eedges.add((t, comm, 'label="%.2f"' % f))
        for t in input_total - itechs:
            dnodes.add((t, None))
            dedges.add((t, comm, None))

        self.__log__('CreateCommodityPartialResults: creating diagrams')
        args = dict(
            inp_commodity=comm,
            period=period,
            resource_node=create_text_nodes(rcnode),
            used_nodes=create_text_nodes(enodes, indent=2),
            unused_nodes=create_text_nodes(dnodes, indent=2),
            used_edges=create_text_edges(eedges, indent=2),
            unused_edges=create_text_edges(dedges, indent=2),
        )
        self.__generate_graph__(commodity_dot_fmt, args, output_name, output_format)
        self.__log__('CreateCommodityPartialResults: graph generated, returning')
        return self.outDir, output_name + '.' + output_format

    # Function for generating the Input Graph
    def create_complete_input_graph(
        self, region, inp_tech=None, inp_comm=None, output_format='svg'
    ):
        self.__log__(
            'createCompleteInputGraph: started with inp_tech = '
            + str(inp_tech)
            + ' and inp_comm = '
            + str(inp_comm)
        )
        output_name = self.qName

        if inp_tech:
            output_name += '_' + str(inp_tech)
            if not os.path.exists(os.path.join(self.outDir, self.folder['tech'])):
                os.makedirs(os.path.join(self.outDir, self.folder['tech']))
            output_name = os.path.join(self.folder['tech'], output_name)
        elif inp_comm:
            output_name += '_' + str(inp_comm)
            if not os.path.exists(os.path.join(self.outDir, self.folder['comm'])):
                os.makedirs(os.path.join(self.outDir, self.folder['comm']))
            output_name = os.path.join(self.folder['comm'], output_name)
        else:
            if not os.path.exists(os.path.join(self.outDir, self.folder['results'])):
                os.makedirs(os.path.join(self.outDir, self.folder['results']))
            output_name = os.path.join(self.folder['results'], output_name)

        if self.region:
            output_name += '_' + self.region

        output_name = os.path.join(self.outDir, output_name)
        if self.greyFlag:
            output_name += '.grey'
        # if (os.path.exists(outputName + '.' + outputFormat)):
        # self.__log__('createCompleteInputGraph: graph already exists at path, returning')
        # return self.outDir, outputName + '.' + outputFormat

        nodes, tech, ltech, to_tech, from_tech = set(), set(), set(), set(), set()

        if DatabaseUtil.is_database_file(self.dbFile):
            res = self.dbUtil.get_commodities_and_tech(inp_comm, inp_tech, region)
        else:
            res = self.dbUtil.read_from_dat_file(inp_comm, inp_tech)

        self.__log__('createCompleteInputGraph: database fetched successfully')
        # Create nodes and edges using the data frames from database
        for i in range(len(res)):
            row = res.iloc[i]
            if row['input_comm'] != 'ethos':
                nodes.add(row['input_comm'])
            else:
                ltech.add(row['tech'])
            nodes.add(row['output_comm'])
            tech.add(row['tech'])

            if row['input_comm'] != 'ethos':
                to_tech.add('"%s"' % row['input_comm'] + '\t->\t"%s"' % row['tech'])
            from_tech.add('"%s"' % row['tech'] + '\t->\t"%s"' % row['output_comm'])

        self.__log__('createCompleteInputGraph: creating diagrams')

        args = dict(
            enodes=''.join('"%s";\n\t\t' % x for x in nodes),
            tnodes=''.join('"%s";\n\t\t' % x for x in tech),
            iedges=''.join('%s;\n\t\t' % x for x in to_tech),
            oedges=''.join('%s;\n\t\t' % x for x in from_tech),
            snodes=';'.join('"%s"' % x for x in ltech),
        )
        self.__generate_graph__(quick_run_dot_fmt, args, output_name, output_format)
        self.__log__('createCompleteInputGraph: graph generated, returning')
        return self.outDir, output_name + '.' + output_format


if __name__ == '__main__':
    input = process_input(sys.argv[1:])
    graph_gen = GraphvizDiagramGenerator(
        input['ifile'], input['scenario_name'], input['region'], out_dir=input['res_dir']
    )
    graph_gen.connect()
    graph_gen.set_graphic_options(grey_flag=input['grey_flag'], splinevar=input['splinevar'])
    if input['scenario_name'] is None:
        res = graph_gen.create_complete_input_graph(
            input['region'], input['inp_technology'], input['inp_commodity']
        )
    elif input['inp_technology'] is None and input['inp_commodity'] is None:
        res = graph_gen.create_main_results_diagram(input['period'], input['region'])
    elif input['inp_commodity'] is None:
        res = graph_gen.create_tech_results_diagrams(
            input['period'], input['region'], input['inp_technology']
        )
    elif input['inp_technology'] is None:
        res = graph_gen.create_commodity_partial_results(
            input['period'], input['region'], input['inp_commodity']
        )
    graph_gen.close()
    print('Check graph generated at ', res[1], ' and all results at ', res[0])
