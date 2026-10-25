"""
This script processes a Temoa database file (SQLite) and converts the data
into two Excel formats: one for human-readable analysis and another
compatible with the IAMC format for integrated assessment modeling.

The script extracts capacity, activity, emissions, and cost data for a
specified scenario, formats it, and saves it to separate sheets in an
Excel workbook. It also creates an aggregated IAMC-compatible Excel file.

Usage:
    python db_to_excel.py -i <input_file.db> -s <scenario_name> [-o <output_file_name>]
"""

import getopt
import itertools
import re
import sqlite3
import sys
from pathlib import Path

import pandas as pd
from pandas import DataFrame


def make_excel(ifile: str | None, ofile: Path | None, scenario: set[str]) -> None:
    """
    Processes a Temoa database to produce human-readable and IAMC-format
    Excel files.
    """
    if ifile is None:
        raise ValueError("You did not specify the input file. Remember to use the '-i' option.")

    file_match = re.search(r'(\w+)\.(\w+)\b', ifile)
    if not file_match:
        raise ValueError(f'The file type {ifile} is not recognized. Use a database file.')

    if ofile is None:
        ofile = Path(file_match.group(1))
        print(f'Look for output in {ofile}_*.xlsx')

    con = sqlite3.connect(ifile)
    scenario_name = scenario.pop()
    ofile = ofile.with_suffix('.xlsx')

    writer = pd.ExcelWriter(
        ofile,
        engine='xlsxwriter',
        engine_kwargs={'options': {'strings_to_formulas': False}},
    )
    workbook = writer.book
    header_format = workbook.add_format({'bold': True, 'text_wrap': True, 'align': 'left'})

    query_all_techs = """
        SELECT DISTINCT efficiency.region, efficiency.tech, Technology.sector
        FROM efficiency
        INNER JOIN Technology ON efficiency.tech = Technology.tech
    """
    all_techs = pd.read_sql_query(query_all_techs, con)

    query_capacity = """
        SELECT region, tech, sector, period, SUM(capacity) as capacity
        FROM output_net_capacity WHERE scenario = ?
        GROUP BY region, tech, sector, period
    """
    df_capacity = pd.read_sql_query(query_capacity, con, params=(scenario_name,))
    for sector in sorted(df_capacity['sector'].unique()):
        df_sector = (
            df_capacity[df_capacity['sector'] == sector]
            .drop(columns=['sector'])
            .pivot_table(values='capacity', index=['region', 'tech'], columns='period')
            .reset_index()
        )
        sector_techs = all_techs[all_techs['sector'] == sector]
        df_sector = pd.merge(
            sector_techs[['region', 'tech']],
            df_sector,
            on=['region', 'tech'],
            how='left',
        )
        df_sector.rename(columns={'region': 'Region', 'tech': 'Technology'}, inplace=True)
        sheet_name = f'Capacity_{sector}'
        df_sector.to_excel(writer, sheet_name=sheet_name, index=False, startrow=1, header=False)
        worksheet = writer.sheets[sheet_name]
        worksheet.set_column('A:A', 10)
        worksheet.set_column('B:B', 10)
        for col, val in enumerate(df_sector.columns.values):
            worksheet.write(0, col, val, header_format)

    query_activity = """
        SELECT region, tech, sector, period, SUM(flow) as vflow_out
        FROM output_flow_out WHERE scenario = ?
        GROUP BY region, tech, sector, period
    """
    df_activity = pd.read_sql_query(query_activity, con, params=(scenario_name,))
    for sector in sorted(df_activity['sector'].unique()):
        df_sector = (
            df_activity[df_activity['sector'] == sector]
            .drop(columns=['sector'])
            .pivot_table(values='vflow_out', index=['region', 'tech'], columns='period')
            .reset_index()
        )
        sector_techs = all_techs[all_techs['sector'] == sector]
        df_sector = pd.merge(
            sector_techs[['region', 'tech']],
            df_sector,
            on=['region', 'tech'],
            how='left',
        )
        df_sector.rename(columns={'region': 'Region', 'tech': 'Technology'}, inplace=True)
        sheet_name = f'Activity_{sector}'
        df_sector.to_excel(writer, sheet_name=sheet_name, index=False, startrow=1, header=False)
        worksheet = writer.sheets[sheet_name]
        worksheet.set_column('A:A', 10)
        worksheet.set_column('B:B', 10)
        for col, val in enumerate(df_sector.columns.values):
            worksheet.write(0, col, val, header_format)

    query_all_emis = """
        SELECT DISTINCT ea.region, ea.tech, ea.emis_comm, t.sector
        FROM emission_activity ea
        INNER JOIN Technology t ON ea.tech = t.tech
    """
    try:
        all_emis_techs = pd.read_sql_query(query_all_emis, con)
    except sqlite3.OperationalError:
        all_emis_techs = pd.DataFrame()

    query_emissions = """
        SELECT region, tech, sector, period, emis_comm, SUM(emission) as emissions
        FROM output_emission WHERE scenario = ?
        GROUP BY region, tech, sector, period, emis_comm
    """
    df_emissions_raw = pd.read_sql_query(query_emissions, con, params=(scenario_name,))
    if not df_emissions_raw.empty:
        df_emissions = df_emissions_raw.pivot_table(
            values='emissions',
            index=['region', 'tech', 'sector', 'emis_comm'],
            columns='period',
        ).reset_index()
        df_emissions = pd.merge(
            all_emis_techs,
            df_emissions,
            on=['region', 'tech', 'sector', 'emis_comm'],
            how='left',
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

    query_costs = """
        SELECT region, oc.tech, t.sector, vintage,
               d_invest + d_var + d_fixed + d_emiss as cost
        FROM output_cost oc
        JOIN Technology t ON oc.tech = t.tech
        WHERE scenario = ?
    """
    df_costs = pd.read_sql_query(query_costs, con, params=(scenario_name,))
    df_costs.columns = ['Region', 'Technology', 'Sector', 'Vintage', 'Cost']
    df_costs.to_excel(writer, sheet_name='Costs', index=False, startrow=1, header=False)
    worksheet = writer.sheets['Costs']
    worksheet.set_column('A:A', 10)
    worksheet.set_column('B:B', 10)
    worksheet.set_column('C:C', 10)
    worksheet.set_column('D:D', 30)
    for col, val in enumerate(df_costs.columns):
        worksheet.write(0, col, val, header_format)

    writer.close()

    df_emissions_raw['variable'] = (
        'Emissions|' + df_emissions_raw['emis_comm'] + '|' + df_emissions_raw['tech']
    )
    df_emissions_iamc = df_emissions_raw.rename(columns={'period': 'year', 'emissions': 'value'})

    df_capacity['variable'] = 'Capacity|' + df_capacity['sector'] + '|' + df_capacity['tech']
    df_capacity_iamc = df_capacity.rename(columns={'period': 'year', 'capacity': 'value'})

    df_activity['variable'] = 'Activity|' + df_activity['sector'] + '|' + df_activity['tech']
    df_activity_iamc = df_activity.rename(columns={'period': 'year', 'vflow_out': 'value'})

    iamc_columns = ['region', 'variable', 'year', 'value']
    df_iamc = pd.concat(
        [
            df_emissions_iamc[iamc_columns],
            df_activity_iamc[iamc_columns],
            df_capacity_iamc[iamc_columns],
        ],
        ignore_index=True,
    )
    df_iamc['unit'] = '?'
    df_iamc['scenario'] = scenario_name

    aggregates_to_add: list[DataFrame] = []
    grouping_cols = ['scenario', 'region', 'year', 'unit']

    emiss_types = df_emissions_raw['emis_comm'].unique()
    for emiss in emiss_types:
        new_variable_name = f'Emissions|{emiss}'
        mask = df_iamc['variable'].str.startswith(f'{new_variable_name}|')
        if mask.any():
            agg = df_iamc[mask].groupby(grouping_cols, as_index=False).sum(numeric_only=True)
            agg['variable'] = new_variable_name
            aggregates_to_add.append(agg)

    sector_types = df_capacity['sector'].unique()
    for var_type, sector in itertools.product(['Activity', 'Capacity'], sector_types):
        new_variable_name = f'{var_type}|{sector}'
        mask = df_iamc['variable'].str.startswith(f'{new_variable_name}|')
        if mask.any():
            agg = df_iamc[mask].groupby(grouping_cols, as_index=False).sum(numeric_only=True)
            agg['variable'] = new_variable_name
            aggregates_to_add.append(agg)

    if aggregates_to_add:
        df_final_iamc = pd.concat([df_iamc, *aggregates_to_add], ignore_index=True)
    else:
        df_final_iamc = df_iamc

    df_final_iamc['model'] = 'Temoa'
    final_cols = ['model', 'scenario', 'region', 'variable', 'unit', 'year', 'value']
    df_final_iamc = df_final_iamc[final_cols]

    base_name = ofile.stem
    excel_pyam_filename = ofile.with_name(f'{base_name}_pyam.xlsx')
    df_final_iamc.to_excel(excel_pyam_filename, index=False)

    con.close()


def get_data(inputs: dict[str, str]) -> None:
    """Parses command-line arguments and calls the main excel creation function."""
    ifile = inputs.get('-i') or inputs.get('--input')
    ofile_str = inputs.get('-o') or inputs.get('--output')
    ofile = Path(ofile_str) if ofile_str else None
    scenario = {s for k, s in inputs.items() if k in ('-s', '--scenario')}

    if not scenario:
        raise ValueError("You must specify a scenario with the '-s' option.")

    make_excel(ifile, ofile, scenario)


if __name__ == '__main__':
    try:
        opts, _ = getopt.getopt(
            sys.argv[1:],
            'hi:o:s:',
            ['help', 'input=', 'output=', 'scenario='],
        )
    except getopt.GetoptError as err:
        print(err)
        print('Use -h or --help for usage instructions.')
        sys.exit(2)

    opts_dict = dict(opts)
    if '-h' in opts_dict or '--help' in opts_dict:
        print(__doc__)
        sys.exit()

    try:
        get_data(opts_dict)
    except (ValueError, FileNotFoundError) as e:
        print(f'Error: {e}')
        sys.exit(2)
