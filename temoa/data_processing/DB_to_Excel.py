import getopt
import itertools
import re
import sqlite3
import sys
from pathlib import Path

import pandas as pd
from pyam import IamDataFrame


def make_excel(ifile, ofile: Path, scenario):
    if ifile is None:
        raise "You did not specify the input file, remember to use '-i' option"
        print(
            'Use as :\n	python DB_to_Excel.py -i <input_file> (Optional -o <output_excel_file_name_only>)\n	Use -h for help.'
        )
        sys.exit(2)
    else:
        file_type = re.search(r'(\w+)\.(\w+)\b', ifile)  # Extract the input filename and extension
    if not file_type:
        print('The file type %s is not recognized. Use a db file.' % ifile)
        sys.exit(2)
    if ofile is None:
        ofile = file_type.group(1)
        print('Look for output in %s_*.xls' % ofile)

    con = sqlite3.connect(ifile)
    cur = con.cursor()  # a database cursor is a control structure that enables traversal over the records in a database
    con.text_factory = str  # this ensures data is explored with the correct UTF-8 encoding
    scenario = scenario.pop()
    ofile = ofile.with_suffix('.xlsx')
    writer = pd.ExcelWriter(
        ofile, engine='xlsxwriter', engine_kwargs={'options': {'strings_to_formulas': False}}
    )

    workbook = writer.book

    header_format = workbook.add_format(
        {
            'bold': True,
            'text_wrap': True,
            'align': 'left',
        }
    )

    query = 'SELECT DISTINCT Efficiency.region, Efficiency.tech, Technology.sector FROM Efficiency \
	INNER JOIN Technology ON Efficiency.tech=Technology.tech'
    all_techs = pd.read_sql_query(query, con)

    query = f"SELECT region, tech, sector, period, sum(capacity) as capacity FROM OutputNetCapacity WHERE scenario= '{scenario}' GROUP BY region, tech, sector, period"
    df_capacity = pd.read_sql_query(query, con)
    for sector in sorted(df_capacity['sector'].unique()):
        df_capacity_sector = df_capacity[df_capacity['sector'] == sector]
        df_capacity_sector = df_capacity_sector.drop(columns=['sector']).pivot_table(
            values='capacity', index=['region', 'tech'], columns='period'
        )
        df_capacity_sector.reset_index(inplace=True)
        sector_techs = all_techs[all_techs['sector'] == sector]
        df_capacity_sector = pd.merge(
            sector_techs[['region', 'tech']], df_capacity_sector, on=['region', 'tech'], how='left'
        )
        df_capacity_sector.rename(columns={'region': 'Region', 'tech': 'Technology'}, inplace=True)
        df_capacity_sector.to_excel(
            writer, sheet_name='Capacity_' + sector, index=False, startrow=1, header=False
        )
        worksheet = writer.sheets['Capacity_' + sector]
        worksheet.set_column('A:A', 10)
        worksheet.set_column('B:B', 10)
        for col, val in enumerate(df_capacity_sector.columns.values):
            worksheet.write(0, col, val, header_format)

    query = (
        "SELECT region, tech, sector, period, sum(flow) as vflow_out FROM OutputFlowOut WHERE scenario='"
        + scenario
        + "' GROUP BY \
	region, tech, sector, period"
    )
    df_activity = pd.read_sql_query(query, con)
    for sector in sorted(df_activity['sector'].unique()):
        df_activity_sector = df_activity[df_activity['sector'] == sector]
        df_activity_sector = df_activity_sector.drop(columns=['sector']).pivot_table(
            values='vflow_out', index=['region', 'tech'], columns='period'
        )
        df_activity_sector.reset_index(inplace=True)
        sector_techs = all_techs[all_techs['sector'] == sector]
        df_activity_sector = pd.merge(
            sector_techs[['region', 'tech']], df_activity_sector, on=['region', 'tech'], how='left'
        )
        df_activity_sector.rename(columns={'region': 'Region', 'tech': 'Technology'}, inplace=True)
        df_activity_sector.to_excel(
            writer, sheet_name='Activity_' + sector, index=False, startrow=1, header=False
        )
        worksheet = writer.sheets['Activity_' + sector]
        worksheet.set_column('A:A', 10)
        worksheet.set_column('B:B', 10)
        for col, val in enumerate(df_activity_sector.columns.values):
            worksheet.write(0, col, val, header_format)

    query = (
        'SELECT DISTINCT EmissionActivity.region, EmissionActivity.tech, EmissionActivity.emis_comm, Technology.sector FROM EmissionActivity \
	INNER JOIN Technology ON EmissionActivity.tech=Technology.tech'
    )
    try:
        all_emis_techs = pd.read_sql_query(query, con)
    except:
        all_emis_techs = {}
    
    query = (
        "SELECT region, tech, sector, period, emis_comm, sum(emission) as emissions FROM OutputEmission WHERE scenario='"
        + scenario
        + "' GROUP BY \
    region, tech, sector, period, emis_comm"
    )
    df_emissions_raw = pd.read_sql_query(query, con)
    if not df_emissions_raw.empty:
        df_emissions = df_emissions_raw.pivot_table(
            values='emissions', index=['region', 'tech', 'sector', 'emis_comm'], columns='period'
        )
        df_emissions.reset_index(inplace=True)
        df_emissions = pd.merge(
            all_emis_techs, df_emissions, on=['region', 'tech', 'sector', 'emis_comm'], how='left'
        )
        df_emissions.rename(
            columns={
                'region': 'Region',
                'tech': 'Technology',
                'emis_comm': 'Emission Commodity',
                'sector': 'Sector',
            },
            inplace=True,
        )
        df_emissions.to_excel(writer, sheet_name='Emissions', index=False, startrow=1, header=False)
        worksheet = writer.sheets['Emissions']
        worksheet.set_column('A:A', 10)
        worksheet.set_column('B:B', 10)
        worksheet.set_column('C:C', 10)
        worksheet.set_column('D:D', 20)
        for col, val in enumerate(df_emissions.columns.values):
            worksheet.write(0, col, val, header_format)

    query = (
        'SELECT region, OutputCost.tech, Technology.sector, vintage, d_invest + d_var + d_fixed + d_emiss FROM OutputCost '
        ' JOIN main.Technology ON OutputCost.tech = main.Technology.tech '
        f" WHERE scenario = '{scenario}'"
    )
    df_costs = pd.read_sql_query(query, con)
    df_costs.columns = ['Region', 'Technology', 'Sector', 'Vintage', 'Cost']
    df_costs.to_excel(writer, sheet_name='Costs', index=False, startrow=1, header=False)
    worksheet = writer.sheets['Costs']
    worksheet.set_column('A:A', 10)
    worksheet.set_column('B:B', 10)
    worksheet.set_column('C:C', 10)
    worksheet.set_column('D:D', 30)
    for col, val in enumerate(df_costs.columns):
        worksheet.write(0, col, val, header_format)

    writer._save()

    # prepare results for IamDataFrame
    df_emissions_raw['scenario'] = scenario
    df_emissions_raw['unit'] = '?'
    df_emissions_raw['variable'] = (
        'Emissions|' + df_emissions_raw['emis_comm'] + '|' + df_emissions_raw['tech']
    )
    df_emissions_raw.rename(columns={'period': 'year', 'emissions': 'value'}, inplace=True)

    df_capacity['scenario'] = scenario
    df_capacity['unit'] = '?'
    df_capacity['variable'] = 'Capacity|' + df_capacity['sector'] + '|' + df_capacity['tech']
    df_capacity.rename(columns={'period': 'year', 'capacity': 'value'}, inplace=True)

    df_activity['scenario'] = scenario
    df_activity['unit'] = '?'
    df_activity['variable'] = 'Activity|' + df_activity['sector'] + '|' + df_activity['tech']
    df_activity.rename(columns={'period': 'year', 'vflow_out': 'value'}, inplace=True)

    # cast results to IamDataFrame and write to xlsx
    columns = ['scenario', 'region', 'variable', 'year', 'value', 'unit']
    _results = pd.concat([df_emissions_raw[columns], df_activity[columns], df_capacity[columns]])
    df = IamDataFrame(_results, model='Temoa')

    emiss = df_emissions_raw['emis_comm'].unique()
    sector = df_capacity['sector'].unique()

    # adding aggregates of emissions for each species
    df.aggregate([f'Emissions|{q}' for q in emiss], append=True)

    # adding aggregates of activity/capacity for each sector
    prod = itertools.product(['Activity', 'Capacity'], sector)
    df.aggregate([f'{t}|{s}' for t, s in prod], append=True)

    # write IamDataFrame to xlsx
    base_name = ofile.name.split('.')[0]
    excel_pyam_filename = ofile.with_name(base_name + '_pyam.xlsx')
    df.to_excel(excel_pyam_filename)

    cur.close()
    con.close()


def get_data(inputs):
    ifile = None
    ofile = None
    scenario = set()

    if inputs is None:
        raise 'no arguments found'

    for opt, arg in inputs.items():
        if opt in ('-i', '--input'):
            ifile = arg
        elif opt in ('-o', '--output'):
            ofile = arg
        elif opt in ('-s', '--scenario'):
            scenario.add(arg)
        elif opt in ('-h', '--help'):
            print(
                'Use as :\n	python DB_to_Excel.py -i <input_file> (Optional -o <output_excel_file_name_only>)\n	Use -h for help.'
            )
            sys.exit()

    make_excel(ifile, ofile, scenario)


if __name__ == '__main__':
    try:
        argv = sys.argv[1:]
        opts, args = getopt.getopt(argv, 'hi:o:s:', ['help', 'input=', 'output=', 'scenario='])
    except getopt.GetoptError:
        print(
            "Something's Wrong. Use as :\n	python DB_to_Excel.py -i <input_file> (Optional -o <output_excel_file_name_only>)\n	Use -h for help."
        )
        sys.exit(2)

    print(opts)

    get_data(dict(opts))
