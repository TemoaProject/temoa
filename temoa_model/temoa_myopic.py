"""
Tools for Energy Model Optimization and Analysis (Temoa):
An open source framework for energy systems optimization modeling

Copyright (C) 2015,  NC State University

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

A complete copy of the GNU General Public License v2 (GPLv2) is available
in LICENSE.txt.  Users uncompressing this from an archive may not have
received this license file.  If not, see <http://www.gnu.org/licenses/>.

This file aims at enabling the myopic/rolling horizon solve using a sqlite
database as input.
The algorithm works by: i) asking the user to enter the number of years that
are to be included in each run, ii) preparing a database from the original
database with the same number of years as the user specified, and solving it.
The assumption is that regardless of the number of years, only the results of
the first period are used in the subsequent run. iii) progressing over the
model time periods by repeating step ii until the end of horizon is reached.
All the results are written in the original database specified in the config file.

"""

import sqlite3
import pandas as pd
from shutil import copyfile
import os
import sys
from IPython import embed as IP
import io

def myopic_db_generator_solver ( self ):
    global db_path_org
    db_path_org = self.options.output
    # original database specified in the ../config_sample file
    con_org = sqlite3.connect(db_path_org)
    cur_org = con_org.cursor()
    table_list = cur_org.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'Output%'").fetchall()
    time_periods = cur_org.execute("SELECT t_periods FROM time_periods WHERE flag='f'").fetchall()
    cur_org.execute("DELETE FROM MyopicBaseyear")
    cur_org.execute("INSERT INTO MyopicBaseyear (year) VALUES ("+str(time_periods[0][0])+")")
    con_org.commit()
    loc1 = max(loc for loc, val in enumerate(self.options.output) if val == '/' or val=='\\')
    loc2 = max(loc for loc, val in enumerate(self.options.output) if val == '.')
    db_name = self.options.output[loc1+1:loc2]
    copyfile(db_path_org, os.path.join(self.options.path_to_data,db_name)+"_blank"+self.options.output[loc2:])

    # group 1 consists of non output tables in which "periods" is a column name
    tables_group1 = ['CostFixed','CostVariable','Demand','EmissionLimit','MaxActivity','MaxCapacity','MinActivity','MinCapacity',\
                    'MaxNewCapacity', 'MinNewCapacity', 'MinNewCapacityGroup', 'MaxNewCapacityGroup', 'MinNewCapacityShare',\
                    'MaxNewCapacityShare','MinAnnualCapacityFactor','MaxAnnualCapacityFactor','MinCapacityGroup','MaxCapacityGroup',\
                    'MaxCapacityShare', 'MinCapacityShare','MinActivityGroup','MaxActivityGroup', 'MinActivityShare', 'MaxActivityShare',\
                    'TechInputSplit','TechInputSplitAverage','TechOutputSplit','CapacityCredit']
    # group 2 consists of non output tables in which "vintage" is a column name except for CostFixed and CostVariable (taken care of above)
    tables_group2 = ['CapacityFactorProcess','CostInvest','DiscountRate', \
                     'Efficiency','EmissionActivity','ExistingCapacity','LifetimeProcess']

    version = int(sys.version[0])

    N = self.options.myopic_periods
    if 1 <= int(N) <= len(time_periods)-2:
        N = int(N)
    else:
        print ("Error: The number of myopic years must between 1 and "+str(len(time_periods)-2))

    for i in range(N-1,len(time_periods)-1):

        print ('Preparing the database for the period(s): '+str([str(time_periods[j][0]) for j in range(i-(N-1),i+1)]))

        new_myopic_name = "_myopic"
        for j in range(i-(N-1),i+1):
            new_myopic_name += "_"+str(time_periods[j][0])

        new_db_loc = os.path.join(self.options.path_to_data, db_name)+new_myopic_name+self.options.output[loc2:]
        copyfile(os.path.join(self.options.path_to_data, db_name) +"_blank"+self.options.output[loc2:], new_db_loc)
        con = sqlite3.connect(new_db_loc)
        cur = con.cursor()
        table_list.sort()

        # ---------------------------------------------------------------
        # Start modifying the Efficiency table
        # ---------------------------------------------------------------
        cur.execute("DELETE FROM Efficiency WHERE vintage > "+str(time_periods[i][0])+";")

        cur.execute("UPDATE Efficiency SET tech = TRIM(tech);") #trim spaces. Need to trim carriage return

        # Delete row from Efficiency if (t,v) retires at the begining of current period (which is time_periods[i][0])
        cur.execute("DELETE FROM Efficiency WHERE tech IN (SELECT tech FROM LifetimeProcess WHERE \
                     LifetimeProcess.life_process+LifetimeProcess.vintage<="+str(time_periods[i-(N-1)][0])+") \
                     AND vintage IN (SELECT vintage FROM LifetimeProcess WHERE LifetimeProcess.life_process+\
                     LifetimeProcess.vintage<="+str(time_periods[i-(N-1)][0])+");")

        # # Delete row from Efficiency if (t,v) retires at the begining of current period (which is time_periods[i][0])
        query = "DELETE FROM Efficiency \
        WHERE (Efficiency.regions, input_comm, Efficiency.tech, vintage, output_comm) IN \
        (SELECT DISTINCT Efficiency.regions, input_comm, Efficiency.tech, vintage, output_comm \
        FROM Efficiency INNER JOIN LifetimeTech ON (LifetimeTech.regions=Efficiency.regions AND LifetimeTech.tech=Efficiency.tech) \
        WHERE Efficiency.vintage + LifetimeTech.life <= "+str(time_periods[i-(N-1)][0])+")\
        AND vintage NOT IN (SELECT vintage FROM LifetimeProcess WHERE LifetimeProcess.tech=Efficiency.tech)"
        cur.execute(query)

        # If row is not deleted via the last two DELETE commands, it might still be invalid for period
        #  time_periods[i][0] since they can have model default lifetime of 40 years.
        cur.execute("DELETE FROM Efficiency WHERE tech IN (SELECT tech FROM Efficiency WHERE \
                    40+Efficiency.vintage<="+str(time_periods[i-(N-1)][0])+") AND \
                    tech NOT IN (SELECT tech FROM LifetimeTech) AND \
                    vintage NOT IN (SELECT vintage FROM LifetimeProcess WHERE LifetimeProcess.tech=Efficiency.tech);")

        # Above commits could break commodity flows defined in the Efficiecny table. We need to delete rows with
        # output commodities that are not generated by any other process. The exception is demand commodities (flag='d')
        iterval = 0
        while len(cur.execute("SELECT * FROM Efficiency WHERE output_comm NOT IN (SELECT input_comm FROM Efficiency)\
                               AND output_comm NOT IN (SELECT comm_name FROM commodities WHERE flag='d');").fetchall()) > 0:

            cur.execute("DELETE FROM Efficiency WHERE output_comm NOT IN (SELECT input_comm FROM Efficiency) \
                     AND output_comm NOT IN (SELECT comm_name FROM commodities WHERE flag='d');")
            iterval+=1
            if iterval>10:
                break

        # ---------------------------------------------------------------
        # Sufficient changes were made on the Efficiency table.
        # Start modifying other tables.
        # ---------------------------------------------------------------
        for table in tables_group1:
            if table in [x[0] for x in table_list]:
                cur.execute("DELETE FROM "+table +" WHERE periods > "+str(time_periods[i][0])+" OR periods < "+str(time_periods[i-(N-1)][0])+";")


        for table in tables_group2:
            if table in [x[0] for x in table_list]:
                if table == 'CostInvest' or table == 'DiscountRate':
                    cur.execute("UPDATE "+table+" SET tech = TRIM(tech);")
                    cur.execute("DELETE FROM "+table +" WHERE vintage > "+str(time_periods[i][0])+";")
                else:
                    cur.execute("DELETE FROM "+table +" WHERE vintage > "+str(time_periods[i][0])+";")

        # time_periods is the only non output table with "t_periods" as a column

        cur.execute("DELETE FROM time_periods WHERE t_periods > "+str(time_periods[i][0])+";")


        # ---------------------------------------------------------------
        # Ensure that linked technologies appear in the Output data tables
        # only if the primary technologies appear as well.
        # Check Output_CapacityByPeriodAndTech and Output_V_Capacity in con_org
        # ---------------------------------------------------------------


        dict_table_column = {}
        dict_table_column['Output_CapacityByPeriodAndTech'] = 't_periods'
        dict_table_column['Output_V_Capacity'] = 'vintage'

        for table in ['Output_CapacityByPeriodAndTech', 'Output_V_Capacity']:
            if i!=(N-1):
                #delete primary_techs where capacity is a small negative value
                query = "DELETE FROM " + table + "  \
                WHERE scenario="+"'"+str(self.options.scenario)+"' AND \
                tech in (SELECT primary_tech FROM LinkedTechs) AND  \
                capacity < 0 AND " + dict_table_column[table] + " = "+str(time_periods[j-1][0])+";"
                cur_org.execute(query)

                #if linked tech exists but primary tech does not
                df_linkedtechs = pd.read_sql_query("SELECT * FROM " + table + "  \
                                                             WHERE scenario="+"'"+str(self.options.scenario)+"' AND \
                                                             tech in (SELECT linked_tech FROM LinkedTechs) AND " + \
                                                             dict_table_column[table] + " = "+str(time_periods[j-1][0])+";", con_org)
                for ind, row in df_linkedtechs.iterrows():
                    primary_tech = pd.read_sql_query("SELECT primary_tech FROM LinkedTechs WHERE primary_region = '" +  row['regions'] + \
                        "' AND linked_tech = '" + row['tech'] + "'", con_org)
                    primary_tech = primary_tech['primary_tech'].values[0]
                    df_primary_tech = pd.read_sql_query("SELECT * FROM " + table + " \
                                                             WHERE scenario="+"'"+str(self.options.scenario)+"' AND \
                                                             tech = '" + primary_tech + "' AND \
                                                             regions = '" + row['regions'] + "' AND " + \
                                                             dict_table_column[table] + " = "+str(time_periods[j-1][0])+";", con_org)
                    if len(df_primary_tech)==0:
                        query = "DELETE FROM " + table + " WHERE scenario="+"'"+str(self.options.scenario)+"' AND \
                        tech = '" + row['tech'] + "' AND regions = '" + row['regions'] + "' AND " + \
                        dict_table_column[table] + " = "+str(time_periods[j-1][0])
                        cur_org.execute(query)
                        if table=='Output_V_Capacity':
                            for aux_table in ['Output_VFlow_Out', 'Output_VFlow_In']:
                                query = "DELETE FROM " + aux_table + " WHERE scenario="+"'"+str(self.options.scenario)+"' AND \
                                tech = '" + row['tech'] + "' AND regions = '" + row['regions'] + "' AND " + \
                                dict_table_column[table] + " = "+str(time_periods[j-1][0])
                                cur_org.execute(query)


                #if primary tech exists but linked tech does not
                df_primarytechs = pd.read_sql_query("SELECT * FROM " + table + "  \
                                                             WHERE scenario="+"'"+str(self.options.scenario)+"' AND \
                                                             tech in (SELECT primary_tech FROM LinkedTechs) AND " + \
                                                             dict_table_column[table] + " = "+str(time_periods[j-1][0])+";", con_org)
                for ind, row in df_primarytechs.iterrows():
                    linked_tech = pd.read_sql_query("SELECT linked_tech FROM LinkedTechs WHERE primary_region = '" +  row['regions'] + \
                        "' AND primary_tech = '" + row['tech'] + "'", con_org)
                    linked_tech = linked_tech['linked_tech'].values[0]
                    df_linked_tech = pd.read_sql_query("SELECT * FROM " + table + " \
                                                             WHERE scenario="+"'"+str(self.options.scenario)+"' AND \
                                                             tech = '" + linked_tech + "' AND \
                                                             regions = '" + row['regions'] + "' AND " + \
                                                             dict_table_column[table] + " = "+str(time_periods[j-1][0])+";", con_org)
                    if len(df_linked_tech)==0:
                        query = "DELETE FROM " + table + " WHERE scenario="+"'"+str(self.options.scenario)+"' AND \
                        tech = '" + row['tech'] + "' AND regions = '" + row['regions'] + "' AND " + \
                        dict_table_column[table] + " = "+str(time_periods[j-1][0])
                        cur_org.execute(query)
                        if table=='Output_V_Capacity':
                            for aux_table in ['Output_VFlow_Out', 'Output_VFlow_In']:
                                query = "DELETE FROM " + aux_table + " WHERE scenario="+"'"+str(self.options.scenario)+"' AND \
                                tech = '" + row['tech'] + "' AND regions = '" + row['regions'] + "' AND " + \
                                dict_table_column[table] + " = "+str(time_periods[j-1][0])
                                cur_org.execute(query)

        # ---------------------------------------------------------------
        # Add the buildups and retirements from the previous period to the ExistingCapacity
        # table. The data is stored in the Output_V_Capacity of the con_org
        # ---------------------------------------------------------------

        if i!=(N-1):
            df_new_ExistingCapacity = pd.read_sql_query("SELECT regions, tech, vintage, capacity FROM Output_V_Capacity \
                                                         WHERE scenario="+"'"+str(self.options.scenario)+"' AND \
                                                         t_periods <= "+str(time_periods[i-(N-1)][0])+";", con_org)
            df_new_ExistingCapacity.columns = ['regions','tech','vintage','exist_cap']
            # Need to remove technologies that have been age-based retired.

            df_new_ExistingCapacity.to_sql('ExistingCapacity',con, if_exists='replace', index=False)

            #Create a copy of the first time period vintages for the two current vintage
            #to prevent infeasibility (if it is not an 'existing' vintage in the
            #original database and if it doesn't already have a current vintage). One example:
            # dummy technologies that have only the first time period vintage (p0)
            for j in range(N-1,-1,-1): #backward loop
                cur.execute("INSERT INTO Efficiency (regions,input_comm,tech,vintage,output_comm,efficiency) \
                             SELECT DISTINCT regions,input_comm,tech,"+str(time_periods[i-j][0])+ \
                             ",output_comm,efficiency FROM Efficiency WHERE tech NOT IN (SELECT tech \
                             FROM Efficiency WHERE vintage < "+str(time_periods[0][0])+") AND tech NOT IN (SELECT \
                             tech FROM Efficiency WHERE vintage >= "+str(time_periods[i-j][0])+");")

            # delete (t,v) from efficiecny table if it doesn't appear in the ExistingCapacity (v is an existing vintage).
            # (note that the model throws a warning if (t,v) is an existing vintage but it doesn't appear in ExistingCapacity)
            cur.execute("DELETE FROM Efficiency \
                         WHERE vintage <= "+str(time_periods[i-N][0])+" AND vintage NOT IN (SELECT \
                         vintage FROM ExistingCapacity WHERE Efficiency.tech=ExistingCapacity.tech AND Efficiency.regions=ExistingCapacity.regions);")

            iterval = 0
            while len(cur.execute("SELECT * FROM Efficiency WHERE output_comm NOT IN (SELECT input_comm FROM Efficiency)\
                                   AND output_comm NOT IN (SELECT comm_name FROM commodities WHERE flag='d');").fetchall()) > 0:

                cur.execute("DELETE FROM Efficiency WHERE output_comm NOT IN (SELECT input_comm FROM Efficiency) \
                         AND output_comm NOT IN (SELECT comm_name FROM commodities WHERE flag='d');")
                iterval+=1
                if iterval>10:
                    break
            # Discard the results associated with time_periods[i-N][0] P time_periods[i-N][0] period in rolling horizon fashion. Otherwise, UNIQUE CONSTRAINT error is thrown.
            # Re Output_Costs, a delete is not needed because in pformat_results.py, future periods costs get added to what is already in the table
            cur_org.execute("DELETE FROM Output_CapacityByPeriodAndTech WHERE scenario="+"'"+str(self.options.scenario)+"' AND t_periods>"+str(time_periods[i-N][0]))
            cur_org.execute("DELETE FROM Output_Emissions WHERE scenario="+"'"+str(self.options.scenario)+"' AND t_periods>"+str(time_periods[i-N][0]))
            cur_org.execute("DELETE FROM Output_VFlow_In WHERE scenario="+"'"+str(self.options.scenario)+"' AND t_periods>"+str(time_periods[i-N][0]))
            cur_org.execute("DELETE FROM Output_VFlow_Out WHERE scenario="+"'"+str(self.options.scenario)+"' AND t_periods>"+str(time_periods[i-N][0]))
            cur_org.execute("DELETE FROM Output_V_Capacity WHERE scenario="+"'"+str(self.options.scenario)+"' AND t_periods>"+str(time_periods[i-N][0]))
            cur_org.execute("DELETE FROM Output_V_NewCapacity WHERE scenario="+"'"+str(self.options.scenario)+"' AND vintage>"+str(time_periods[i-N][0]))
            cur_org.execute("DELETE FROM Output_V_RetiredCapacity WHERE scenario="+"'"+str(self.options.scenario)+"' AND t_periods>"+str(time_periods[i-N][0]))
            cur_org.execute("DELETE FROM Output_Curtailment WHERE scenario="+"'"+str(self.options.scenario)+"' AND t_periods>"+str(time_periods[i-N][0]))
            con_org.commit()

        # ---------------------------------------------------------------
        # The Efficiency table is now ready. Continue modifying other tables.
        # ---------------------------------------------------------------
        for table in table_list:
            if table[0] == 'Efficiency': continue
            try:
                if table[0]=='LinkedTechs':
                    cur.execute("DELETE FROM LinkedTechs WHERE primary_tech NOT IN (SELECT DISTINCT(tech) FROM Efficiency)")
                    cur.execute("DELETE FROM LinkedTechs WHERE linked_tech NOT IN (SELECT DISTINCT(tech) FROM Efficiency)")
                cur.execute("UPDATE "+str(table[0])+" SET tech = TRIM(tech, CHAR(37,10));")
                # If t doesn't exist in Efficiency table after the deletions made above,
                # it is deleted from other tables.
                cur.execute("DELETE FROM "+str(table[0])+" WHERE tech NOT IN (SELECT tech FROM Efficiency);")
                cursor = con.execute("SELECT * FROM "+str(table[0]))
                names = list(map(lambda x: x[0], cursor.description))
                if 'regions' in names:
                    query = "DELETE FROM "+str(table[0])+" WHERE (regions, tech) NOT IN (SELECT DISTINCT regions, tech FROM Efficiency) \
                    AND regions!='global'"
                    cur.execute(query)
                    query = "DELETE FROM "+str(table[0])+" WHERE tech NOT IN (SELECT tech FROM Efficiency) \
                    AND regions='global'"
                    cur.execute(query)

                if 'vintage' in names:
                    if table[0]!='ExistingCapacity':
                        for j in range(N-1,-1,-1):
                            names = list(map(lambda x: x[0], cursor.description))
                            names = [str(time_periods[i-j][0]) if x=='vintage' else x for x in names]
                            query = "SELECT DISTINCT "+",".join(names)+\
                                    " FROM "+table[0]+" WHERE tech NOT IN (SELECT tech FROM "+table[0]+\
                                    " WHERE vintage<"+str(time_periods[0][0])+") AND tech NOT IN (SELECT tech FROM "+\
                                    table[0]+" WHERE vintage >= "+str(time_periods[i-j][0])+");"
                            df_table = cur.execute(query).fetchall()
                            if df_table == []: continue
                            df_table = pd.read_sql_query(query, con)
                            if table[0] == 'EmissionActivity':
                                filter_list = names[:names.index(str(time_periods[i-j][0]))+2]
                            else:
                                filter_list = names[:names.index(str(time_periods[i-j][0]))+1]
                            df_table = df_table.drop_duplicates(subset=filter_list, keep='last')
                            df_table.columns = ['vintage' if x==str(time_periods[i-j][0]) else x for x in df_table.columns]
                            df_table.to_sql(str(table[0]),con, if_exists='append', index=False)

                    # For these two table we only want current vintages.
                    if table[0] == 'CostInvest' or table[0] == 'DiscountRate':
                        cur.execute("DELETE FROM "+str(table[0])+" WHERE vintage > "+str(time_periods[i][0])+" OR vintage < "+str(time_periods[i-(N-1)][0])+";")
                    if table[0] == 'CostVariable' or table[0] == 'CostFixed':
                        cur.execute("DELETE FROM "+str(table[0])+" WHERE periods < vintage;")
                    # If (t,v) is not found in the Efficiecny table, deelte it from all the other tables
                    # For the EmissionActivity, (i,t,v,o) tuple must be checked.
                    if table[0] == 'EmissionActivity':
                        cur.execute("DELETE FROM EmissionActivity WHERE regions || input_comm || tech || vintage || output_comm \
                                    NOT IN (SELECT regions || input_comm || tech || vintage || output_comm FROM Efficiency)")
                    else:
                        cur.execute("DELETE FROM "+str(table[0])+" WHERE tech IN (SELECT tech FROM Efficiency) AND vintage \
                                 NOT IN (SELECT vintage FROM Efficiency WHERE Efficiency.tech="+str(table[0])+".tech \
                                 AND Efficiency.regions="+str(table[0])+".regions);")
            #except:
            #    raise Exception(table[0],j)

            except:
            	pass

        cur.execute("UPDATE commodities SET comm_name = TRIM(comm_name, CHAR(10,13,37))")
        # delete unused commodities otherwise the model throws an error

        cur.execute("DELETE FROM commodities WHERE flag!='e' AND comm_name NOT IN (SELECT input_comm from Efficiency UNION SELECT output_comm from Efficiency);")
        cur.execute("INSERT INTO `time_periods` (t_periods,flag) VALUES ("+str(time_periods[i+1][0])+",'f');")
        cur.execute("UPDATE `time_periods` SET flag='e' WHERE t_periods < "+str(time_periods[i-(N-1)][0]))



        # --------------------------------------------------------------------------------------------------
        # Update the maximum resource table to include flows that already contribute to resource consumption
        # --------------------------------------------------------------------------------------------------
        if (i!=(N-1)) & ('MaxResource' in [x[0] for x in table_list]):
            resource_constraints_org = pd.read_sql_query("SELECT regions, tech, maxres FROM MaxResource", con_org)
            for ind,row in resource_constraints_org.iterrows():
                df_existing_resources = pd.read_sql_query("SELECT sum(vflow_out) FROM Output_VFlow_Out \
                                                        WHERE regions='" + row['regions'] + "' AND \
                                                        tech='" + row['tech'] + "' AND \
                                                        scenario="+"'"+str(self.options.scenario)+"' AND \
                                                        vintage < "+str(time_periods[i-(N-1)][0]), con_org)
                try:
                    updated_resource = row['maxres'] - df_existing_resources.iloc[0,0]
                    query = "UPDATE MaxResource SET maxres=" + str(updated_resource) + " WHERE regions='"\
                    + row['regions'] + "' AND tech='" + row['tech'] + "'"
                    cur.execute(query)
                except:
                    pass


        con.commit()
        con.close()

        # looks like the VACUUM command does not work well
        # in python 3 if embeded in line 180. To avoid potential
        # errors, the database is closed and re-opened.
        con = sqlite3.connect(new_db_loc, isolation_level=None)
        cur = con.cursor()
        cur.execute("VACUUM")
        con.commit()
        con.close()
        # ---------------------------------------------------------------
        # the database is ready. It is run via a temporary config file in
        # a perfect foresight fashion.
        # ---------------------------------------------------------------
        new_config = os.path.join(os.getcwd(), "temoa_model", "config_sample")+new_myopic_name
        if version<3:
            ifile = io.open(os.path.join(os.getcwd(), "temoa_model", "config_sample"), encoding='utf-8')
        else:
            ifile = open(os.path.join(os.getcwd(), "temoa_model", "config_sample"), encoding='utf-8')

        ofile = open(new_config,'w')
        for line in ifile:
            new_line = line.replace("--input=data_files/"+db_name, "--input=data_files/"+db_name+new_myopic_name)
            # the temporary config file is created from the original config file. Since for individual periods we are
            # going to have a standard run, '--rollinghorizon' needs to be commented out.
            new_line = new_line.replace("--myopic","#--myopic")
            if version<3:
                ofile.write(new_line.encode('utf-8'))
            else:
                ofile.write(new_line)

        ifile.close()
        ofile.close()
        os.system("python temoa_model/ --config=temoa_model/config_sample"+new_myopic_name)
        # delete the temporary config file
        os.remove(new_config)
        if not self.options.KeepMyopicDBs:
            os.remove(new_db_loc)
            os.remove(os.path.join(self.options.path_to_data, db_name) +new_myopic_name+".dat")


    os.remove(os.path.join(self.options.path_to_data,db_name)+"_blank"+self.options.output[loc2:])
