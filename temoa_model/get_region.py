import sqlite3
from collections import OrderedDict


def get_region_list(db_file):
    region_list = {}
    con = sqlite3.connect(db_file)
    cur = con.cursor()  # a database cursor is a control structure that enables traversal over the records in a database
    con.text_factory = str  # this ensures data is explored with the correct UTF-8 encoding

    cur.execute("SELECT DISTINCT regions FROM regions")
    for row in cur:
        x = row[0]
        region_list[x] = x

    cur.close()
    con.close()

    return OrderedDict(sorted(region_list.items(), key=lambda x: x[1]))