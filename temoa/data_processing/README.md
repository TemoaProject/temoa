# Overview

This folder contains files used to manage Temoa input/output data. Included files are:

1. `DB_to_Excel.py/`
Python script that queries database output tables to create an Excel file containing scenario-specific results.

2. `Make_Graphviz.py/`
Python script that creates a Graphviz diagram for the database.
The most basic way to use graphviz is to view the full energy system map:
```$ python MakeGraphviz.py -i temoa_utopia.sqlite```  Other options include a capacitated
flow graph for a specific period:  ```-i ../../data_files/utopia.sqlite -r utopia -s <scenario name> -c -y 2010```
note how this input file passes a relative link up to the data_files directory, assuming standard location in the project


3. `Network_diagrams.ipynb/`
Notebook to interactively view network diagrams for a user-specified database.
Create and activate the Temoa environment, as follows:

	```$ conda env create```

	```$ source activate temoa-py3```

	Once the Temoa environment is created and activated, enable the following extensions from from the command line.
	This will need to be done only once, before using notebooks within the Temoa environment.

	```(temoa-py3) $ jupyter nbextension enable init_cell/main```

	```(temoa-py3) $ jupyter nbextension enable hide_input/main```

	Once these extensions are enabled, navigate to the `temoa/data_processing/` folder and then open notebooks as follows.

	```(temoa-py3) $ jupyter notebook```

	Navigate to the `Network_diagrams.ipynb/` file and select technology/commodity options to interactively view their network diagrams.
	The notebook also includes an interactive technology/commodity lookup tool.
	The "Toggle selected cell input display" button (below and to the right of the Help menu) can be used to view hidden code cells.
