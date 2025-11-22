import getopt
import os
import re
import sqlite3
import sys
from collections import OrderedDict


def get_tperiods(inp_f):
    file_ty = re.search(r'(\w+)\.(\w+)\b', inp_f)  # Extract the input filename and extension

    if not file_ty:
        raise 'The file type %s is not recognized.' % inp_f

    elif file_ty.group(2) not in ('db', 'sqlite', 'sqlite3', 'sqlitedb'):
        raise Exception('Please specify a database for finding scenarios')

    periods_list = {}
    periods_set = set()

    con = sqlite3.connect(inp_f)
    cur = con.cursor()  # a database cursor is a control structure that enables traversal over
    # the records in a database
    con.text_factory = str  # this ensures data is explored with the correct UTF-8 encoding

    print(inp_f)
    cur.execute('SELECT DISTINCT scenario FROM output_flow_out')
    x = []
    for row in cur:
        x.append(row[0])
    for y in x:
        cur.execute(
            "SELECT DISTINCT period FROM output_flow_out WHERE scenario is '" + str(y) + "'"
        )
        periods_list[y] = []
        for per in cur:
            z = per[0]
            periods_list[y].append(z)

    cur.close()
    con.close()
    return dict(OrderedDict(sorted(periods_list.items(), key=lambda x: x[1])))


def get_scenario(inp_f):
    file_ty = re.search(r'(\w+)\.(\w+)\b', inp_f)  # Extract the input filename and extension

    if not file_ty:
        raise 'The file type %s is not recognized.' % inp_f

    elif file_ty.group(2) not in ('db', 'sqlite', 'sqlite3', 'sqlitedb'):
        raise Exception('Please specify a database for finding scenarios')

    scene_list = {}
    scene_set = set()

    con = sqlite3.connect(inp_f)
    cur = con.cursor()  # a database cursor is a control structure that enables traversal over
    # the records in a database
    con.text_factory = str  # this ensures data is explored with the correct UTF-8 encoding

    print(inp_f)
    cur.execute('SELECT DISTINCT scenario FROM output_flow_out')
    for row in cur:
        x = row[0]
        scene_list[x] = x

    cur.close()
    con.close()
    return dict(OrderedDict(sorted(scene_list.items(), key=lambda x: x[1])))


def get_comm(inp_f, db_dat):
    comm_list = {}
    comm_set = set()
    is_query_empty = False

    if not db_dat:
        con = sqlite3.connect(inp_f)
        cur = con.cursor()  # a database cursor is a control structure that enables traversal over
        # the records in a database
        con.text_factory = str  # this ensures data is explored with the correct UTF-8 encoding

        print(inp_f)
        cur.execute('SELECT DISTINCT name FROM Commodity')

        for row in cur:
            is_query_empty = True
            if row[0] != 'ethos':
                x = row[0]
                comm_list[x] = x

        if not is_query_empty:
            cur.execute(
                'SELECT input_comm FROM output_flow_out UNION SELECT output_comm FROM '
                'output_flow_out'
            )

        for row in cur:
            if row[0] != 'ethos':
                x = row[0]
                comm_list[x] = x

        cur.close()
        con.close()

    else:
        eff_flag = False
        with open(inp_f) as f:
            for line in f:
                if eff_flag is False and re.search(
                    r'^\s*param\s+efficiency\s*[:][=]', line, flags=re.I
                ):
                    # Search for the line param efficiency := (The script recognizes the
                    # commodities specified in this section)
                    eff_flag = True
                elif eff_flag:
                    line = re.sub('[#].*$', ' ', line)
                    if re.search(r'^\s*;\s*$', line):
                        break  #  Finish searching this section when encounter a ';'
                    if re.search(r'^\s+$', line):
                        continue
                    line = re.sub(r'^\s+|\s+$', '', line)
                    row = re.split(r'\s+', line)
                    if row[0] != 'ethos':
                        comm_set.add(row[0])
                    comm_set.add(row[3])

        if eff_flag is False:
            print(
                'Error: The efficiency Parameters cannot be found in the specified file - ' + inp_f
            )
            sys.exit(2)

        for x in comm_set:
            comm_list[x] = x

    return OrderedDict(sorted(comm_list.items(), key=lambda x: x[1]))


def get_tech(inp_f, db_dat):
    tech_list = {}
    tech_set = set()
    is_query_empty = False

    if not db_dat:
        con = sqlite3.connect(inp_f)
        cur = con.cursor()  # a database cursor is a control structure that enables traversal over
        # the records in a database
        con.text_factory = str  # this ensures data is explored with the correct UTF-8 encoding

        print(inp_f)
        cur.execute('SELECT DISTINCT tech FROM Technology')

        for row in cur:
            is_query_empty = True
            x = row[0]
            tech_list[x] = x

        if not is_query_empty:
            cur.execute('SELECT DISTINCT tech FROM output_flow_out')

        for row in cur:
            x = row[0]
            tech_list[x] = x

        cur.close()
        con.close()

    else:
        eff_flag = False
        with open(inp_f) as f:
            for line in f:
                if eff_flag is False and re.search(
                    r'^\s*param\s+efficiency\s*[:][=]', line, flags=re.I
                ):
                    # Search for the line param efficiency := (The script recognizes the
                    # commodities specified in this section)
                    eff_flag = True
                elif eff_flag:
                    line = re.sub('[#].*$', ' ', line)
                    if re.search(r'^\s*;\s*$', line):
                        break  #  Finish searching this section when encounter a ';'
                    if re.search(r'^\s+$', line):
                        continue
                    line = re.sub(r'^\s+|\s+$', '', line)
                    row = re.split(r'\s+', line)
                    tech_set.add(row[1])

        if eff_flag is False:
            print(
                'Error: The efficiency Parameters cannot be found in the specified file - ' + inp_f
            )
            sys.exit(2)

        for x in tech_set:
            tech_list[x] = x

    return OrderedDict(sorted(tech_list.items(), key=lambda x: x[1]))


def is_db_overwritten(db_file, inp_dat_file):
    if os.path.basename(db_file) == '0':
        return False

    try:
        con = sqlite3.connect(db_file)
    except:
        return False
    cur = con.cursor()  # A database cursor enables traversal over DB records
    con.text_factory = str  # This ensures data is explored with UTF-8 encoding

    # Copy tables from Input File to DB file.
    # IF output file is empty database.
    cur.execute('SELECT * FROM Technology')
    is_db_empty = False  # False for empty db file
    for elem in cur:
        is_db_empty = True  # True for non-empty db file
        break
    # This file could be schema with populated results from previous run. Or it could be a normal
    # db file.
    if is_db_empty:
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='input_file';")
        does_input_file_table_exist = False
        for i in cur:  # This means that the 'input_file' table exists in db.
            does_input_file_table_exist = True
        if does_input_file_table_exist:  # This block distinguishes normal database from schema.
            # This is schema file.
            cur.execute("SELECT file FROM input_file WHERE id is '1';")
            for i in cur:
                tagged_file = i[0]
            tagged_file = re.sub('["]', '', tagged_file)

            cur.close()
            con.close()

            if tagged_file == inp_dat_file.split('.')[0] + '.dat':
                # If Input_file name matches, no overwriting.
                return False
            else:
                # If not a match, delete output tables and update input_file. Return True
                return True

    cur.close()
    con.close()

    return False


def help_user():
    print(
        """Use as:
    python get_comm_tech.py -i (or --input) <input filename>
    | -c (or --comm) To get a dict of commodities
    | -t (or --tech) To get a dict of commodities
    | -s (or --scenario) To get a dict of scenarios
    | -p (or --period) To get a dict of time periods
    | -h (or --help) """
    )


def get_info(inputs):
    inp_file = None
    tech_flag = False
    comm_flag = False
    scene = False
    db_or_dat = False  # Means db by default
    tperiods_flag = False

    if inputs is None:
        raise Exception('no arguments found')

    for opt, arg in inputs.items():
        print(f'{opt} == {arg}')

        if opt in ('-i', '--input'):
            inp_file = arg
        elif opt in ('-c', '--comm'):
            comm_flag = True
        elif opt in ('-t', '--tech'):
            tech_flag = True
        elif opt in ('-s', '--scenario'):
            scene = True
        elif opt in ('-p', '--period'):
            tperiods_flag = True
        elif opt in ('-h', '--help'):
            help_user()
            sys.exit(2)

    if inp_file is None:
        raise Exception('Input file not specified')

    if tperiods_flag:
        if comm_flag or scene or tech_flag:
            raise Exception('can only use one flag at a time')

    if (
        (comm_flag and tech_flag)
        or (comm_flag and scene)
        or (scene and tech_flag)
        or (comm_flag and tech_flag and scene)
    ):
        raise Exception('can only use one flag at a time')
    if not comm_flag and not tech_flag and not scene and not tperiods_flag:
        raise Exception('flag not specified')

    file_ty = re.search(r'(\w+)\.(\w+)\b', inp_file)  # Extract the input filename and extension

    if not file_ty:
        raise Exception(f'The file type {file_ty} is not recognized.')

    elif file_ty.group(2) in ('db', 'sqlite', 'sqlite3', 'sqlitedb'):
        db_or_dat = False

    elif file_ty.group(2) in ('dat', 'txt'):
        db_or_dat = True

    else:
        print(
            'The input file type %s is not recognized. Please specify a database or a text file.'
            % inp_file
        )
        sys.exit(2)

    if comm_flag:
        return get_comm(inp_file, db_or_dat)

    if tech_flag:
        return get_tech(inp_file, db_or_dat)

    if tperiods_flag:
        return get_tperiods(inp_file)

    if scene:
        if db_or_dat:
            raise Exception('Please specify a database for finding scenarios')
        return get_scenario(inp_file)


if __name__ == '__main__':
    try:
        argv = sys.argv[1:]
        opts, args = getopt.getopt(
            argv, 'hctsi:p', ['help', 'comm', 'tech', 'scenario', 'input=', 'period']
        )

        print(opts)

    except getopt.GetoptError:
        help_user()
        sys.exit(2)

    print(get_info(dict(opts)))
