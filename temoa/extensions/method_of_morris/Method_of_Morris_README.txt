
NOTE:  The below README is OUTDATED but it describes the history of MM application.
Current users should refer to the MM_README.md file in this directory for how-to and
walk-through on the example provided in data_files!

-----------------------
Method of Morris README
-----------------------

This README is based on the following Temoa Google Group post:
https://groups.google.com/forum/#!topic/temoa-project/SEqlvJOpnb0


1. Install SALib (pip install SALib). It's an open source python sensitivity analysis library.

2. Download the attached file and put it in your "temoa-energysystem" directory. Basically what this script does, is reading the baseline values of the parameters you want to do the sensitivity analysis on (say price of a specific fuel or technology), perturbing them by -+10% and creating text files which include all the parameters and their corresponding ranges of change (0.9*baseline=lower bound, 1.1*baseline=upper bound), sending the text files to SALib to generate the sampling matrix (param_values parameter in the script), running the model with the sampling matrix as many times as needed (you can control the number of the runs changing the N in line 141), reading the objective function values and CO2 emissions from the database for each run and sending their corresponding values to SALib to do the analysis.

3. Currently the sensitivity analysis can be done only on the parameters in the tables: cost_invest, cost_variable and efficiency. You need to add a new column in your sqlite database for these tables. You do this by just executing these 3 lines:

ALTER TABLE 'cost_invest' ADD 'MMAnalysis'
ALTER TABLE 'cost_variable' ADD 'MMAnalysis'
ALTER TABLE 'efficiency' ADD 'MMAnalysis'

4. Once this additional column is added for the 3 tables, you need to add names to the cell under MMAnalysis column which corresponds to the parameters you want to do the sensitivity analysis for. For example in Utopia case study, suppose you want to do the sensitivity analysis on gasoline, diesel and coal prices.

Here, parameters with the same text in the MMAnalysis column are seen as "groups" of parameters and are changed simultaneously during the sampling process. If you don't want to use groups, you can put different names on each parameters and the MM only considers the sensitivity with respect to that specific variable. The former gives the sensitivity for a group of parameters.

5. Change your database name to "Method_of_Morris.sqlite" and like other databases ran by Temoa, put it in db_io/dbs directory.

After the changes on the database are done, you are set to run the script: python morris.py (make sure your run it from temoa-energysystem directory)
The output of the method is mu_stars for each and every group of parameters (in the example 3) and their 95% confidence intervals. mu_star_i implies the expected change in the model objective (could be objective function or cumulative CO2 emission depending on your analysis) given the range of the change in the group of parameters i. A .csv file is generated after running the script which contains the mu_stars and their confidence intervals. Also the sensitivity results on objective function will be shown on the terminal.

--------------------------------------------------
Other implementation-related issues you should know:

1. The scripts parallelizes all the cores in your machine when running the model. It might not be significant in small case studies for bigger models, using all the cores saves the time need to run the model.
2. It's very important that the reference to your input and output sqlite files in the config_sample file (--input=db_io/dbs/Method_of_Morris.sqlite and --output=db_io/dbs/Method_of_Morris.sqlite) are placed in the 14th and 21nd lines of config_sample file.
3. Since you are using sqlite and not .db, change all the ".db" texts in the attached script to ".sqlite".
4. I would suggest keeping num_levels=4, grid_jump=2. For this setting should be greater than 10. The total number of the runs is N*(number of groups+1).
