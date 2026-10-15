# TEMOA
## Model features

This is an extended version of the [TEMOA](https://temoacloud.com/) (Tools for Energy Modeling Optimization and Analysis) energy system modeling framework.

This model version is maintained by the by the [MAHTEP Group](http://www.mahtep.polito.it/) at the Department of Energy of [Politecnico di Torino](https://www.polito.it/) and at the Department of Economics and Statistic of [Università degli Studi di Torino](https://www.unito.it/).
The group is lead by Prof. [Laura Savoldi](http://www.mahtep.polito.it/people/coordinators/savoldi_laura) ad Prof. [Valeria di Cosmo](http://www.mahtep.polito.it/people/coordinators/di_cosmo_valeria). For any communication related to this TEMOA version, please write to [matteo.nicoli@polito.it](mailto:matteo.nicoli@polito.it).

The public model instances maintained by the MAHTEP Group are:
* [TEMOA-Europe](https://github.com/MAHTEP/TEMOA-Europe)
* [TEMOA-Italy](https://github.com/MAHTEP/TEMOA-Italy)
* [TEMOA-Piedmont](https://github.com/MAHTEP/TEMOA-Piedmont)
* [TEMOA-NO4](https://github.com/MAHTEP/TEMOA-NO4)

Below, the list of publications in which this version was used:
1. M. Cais, M. Nicoli, M. Gandiglio, L. Savoldi et al., “Hybrid superconducting energy pipelines: key cost thresholds and system implications for Italy,” Int. J. Hydrogen Energy, vol. 210, no. 153627, 2026, doi: 10.1016/j.ijhydene.2026.153627.
2. A. Mastrantuono, M. Nicoli, V. Di Cosmo, D. Mosso, A. Rodrigo de Queiroz, and L. Savoldi, “Key determinants of nuclear fission competitiveness and implications of its potential restart for the Italian power system,” Energy, vol. 360, p. 141475, Sep. 2026, doi: 10.1016/j.energy.2026.141475.
3. M. Nicoli et al., “A framework for global sensitivity analysis in long-term energy systems planning using optimal transport,” Energy, vol. 338, p. 138788, Nov. 2025, doi: 10.1016/J.ENERGY.2025.138788.
4. V. Di Cosmo, M. Nicoli, D. Cottafava, and A. Vai, “Social Acceptability and Transport: An Energy System–Optimisation- Based Analysis of the European Case,” Economics of Energy and Environmental Policy, Jun. 2026, doi: 10.5547/2160-5890.15.1.MNIC.
5. M. Nicoli, “An energy planning perspective about the multi-sectorial synergies and implications of the energy transition,” PhD Thesis, Politecnico di Torino, Turin, 2025. Accessed: Jul. 07, 2025. [Online]. Available: https://iris.polito.it/handle/11583/3001281
6. F. Amir Kavei, M. E. Alfano, M. Nicoli, F. Quatraro, and L. Savoldi, “Integrated Water-Energy Modeling in TEMOA Energy System Optimization Model: Pantelleria Case Study,” Energy Nexus, vol. 18, p. 100461, 2025, doi: 10.1016/J.NEXUS.2025.100461.
7. A. Vai, G. Colucci, M. Nicoli, and L. Savoldi, “May the availability of critical raw materials affect the security of energy systems? An analysis for risk-aware energy planning with TEMOA-Italy,” Mater Today Energy, vol. 48, no. 101805, 2025, doi: 10.1016/j.mtener.2025.101805.
8. F. Amir Kavei, M. Nicoli, F. Quatraro, and L. Savoldi, “Enhancing energy transition with open-source regional energy system optimization models: TEMOA-Piedmont,” Energy Convers Manag, vol. 327, p. 119536, Mar. 2025, doi: 10.1016/J.ENCONMAN.2025.119536.
9. M. Nicoli, G. Colucci, V. Di Cosmo, D. Lerede, and L. Savoldi, “Evaluating the impact of hurdle rates on the Italian energy transition through TEMOA,” Appl Energy, vol. 377PC, no. 124633, 2024, doi: 10.1016/j.apenergy.2024.124633.
10. M. Nicoli, V. A. D. Faria, A. R. de Queiroz, and L. Savoldi, “Modeling energy storage in long-term capacity expansion energy planning: an analysis of the Italian system,” J Energy Storage, vol. 101PA, no. 113814, 2024, doi: 10.1016/j.est.2024.113814.
11. M. Nicoli et al., “Enabling Coherence Between Energy Policies and SDGs Through Open Energy Models: The TEMOA-Italy Example,” in Aligning the Energy Transition with the Sustainable Development Goals: Key Insights from Energy System Modelling, M. Labriet, K. Espegren, G. Giannakidis, and B. O’Gallachoir, Eds., Springer, 2024, pp. 97–118. doi: 10.1007/978-3-031-58897-6_5.
12. D. Mosso, G. Colucci, D. Lerede, M. Nicoli, M. S. Piscitelli, and L. Savoldi, “How much do carbon emission reduction strategies comply with a sustainable development of the power sector?,” Energy Reports, vol. 11, pp. 3064–3087, Jun. 2024, doi: 10.1016/J.EGYR.2024.02.056.
13. G. Colucci, D. Lerede, M. Nicoli, and L. Savoldi, “A dynamic accounting method for CO2 emissions to assess the penetration of low-carbon fuels: application to the TEMOA-Italy energy system optimization model,” Appl Energy, vol. 352, no. 121951, Dec. 2023, doi: 10.1016/j.apenergy.2023.121951.
14. M. Nicoli, “A TIMES-like open-source model for the Italian energy system,” Politecnico di Torino, Turin, 2021. Accessed: Jul. 05, 2022. [Online]. Available: https://webthesis.biblio.polito.it/18850/
15. M. Nicoli, F. Gracceva, D. Lerede, and L. Savoldi, “Can We Rely on Open-Source Energy System Optimization Models? The TEMOA-Italy Case Study,” Energies (Basel), vol. 15, no. 18, p. 6505, Sep. 2022, doi: 10.3390/en15186505.


## Installation Guide
This guide provides step-by-step instructions to install the required software for running the TEMOA energy system optimization model, assuming the user is eligible for requesting a Gurobi academic license.

### Step 1: Install Anaconda
Anaconda is a Python distribution that simplifies package management and deployment.

1. Download Anaconda from [https://www.anaconda.com/download](https://www.anaconda.com/download).
2. Select the appropriate version for your operating system (Windows, macOS, or Linux).
3. Follow the installation instructions provided on the website.
4. During installation, check the option to add Anaconda to your system's PATH.
5. To verify the installation, open a terminal (Command Prompt on Windows, Terminal on macOS/Linux) and type:
   ```sh
   conda --version
   ```
   If installed correctly, this will return the Anaconda version number.

### Step 2: Download the TEMOA source code (MAHTEP version)

1. Go to the MAHTEP version of TEMOA on GitHub: [https://github.com/MAHTEP/TEMOA](https://github.com/MAHTEP/TEMOA).
2. Download the repository as a ZIP file by clicking on "Code" > "Download ZIP".
3. Alternatively, you can clone the repository using Git:
   ```sh
   git clone https://github.com/MAHTEP/TEMOA.git
   ```
4. Extract the ZIP file to a folder on your computer.
5. Rename the folder with the model source code as "TEMOA".

### Step 3: Create the Conda Virtual Environment
A virtual environment ensures that dependencies are installed in an isolated environment.

1. Open a terminal (Command Prompt on Windows, Terminal on macOS/Linux).
2. Navigate to the extracted TEMOA directory using the `cd` command:
   ```sh
   cd ../TEMOA/environments/temoa
   ```
3. Create the virtual environment:
   ```sh
   conda env create -f temoa.yml
   ```
4. Activate the environment:
   ```sh
   conda activate temoa
   ```
5. To check if the environment is activated, type:
   ```sh
   conda env list
   ```
   The `temoa` environment should be marked with an asterisk `*`.

An alternative virtual environment is required to run TEMOA with stochastic optimization. The guide to install this environment and the necessary steps required to modify accordingly the TEMOA source code are located at:
```
..TEMOA/environments/temoa-stochastic
```

### Step 4: Install Gurobi and Register an Academic License
Gurobi is required to solve optimization models in TEMOA.

1. Download Gurobi from [https://www.gurobi.com/downloads/](https://www.gurobi.com/downloads/).
2. Follow the installation instructions for your operating system.
3. After installation, register for an academic named-user license at [https://www.gurobi.com/academia/academic-program-and-licenses/](https://www.gurobi.com/academia/academic-program-and-licenses/).
4. Ensure that your computer is connected to the academic network during license registration.
5. Run the following command (provided by the Gurobi website during the license request) to register the license key:
   ```sh
   grbgetkey YOUR_LICENSE_KEY
   ```
6. If successful, Gurobi should now be ready to use.

### Step 5: Running a TEMOA Simulation
To run a TEMOA simulation, the user can customize the settings in the configuration file located at:
```
../TEMOA/temoa_model/config_sample
```

In the `config_sample` file, users can specify:
- **Input database**: The SQLite database containing the model instance.
- **Output database**: The database where results will be stored.
- **Scenario name**: The scenario name sed to store results.
- **Path to data**: The path to the folder containing the input and output database.
- **Optional settings**, including those necessary to run TEMOA with:
  - *MGA (Modeling to Generate Alternatives)*: Used to explore alternative solutions.
  - *MOO (Multi-Objective Optimization)*: Used for multi-objective optimization runs.
  - *MGPA (Modeling to Generate near-Pareto-optimal Alternatives)*: Used to explore near-pareto optimal alternatives (it combines MOO with MGA).


To test that TEMOA is working correctly, users can optimize the `temoa_utopia.sqlite` database, which represents a simple model instance developed for testing purposes.

After customizing the settings, navigate to the extracted TEMOA directory using the `cd` command:
```sh
cd ../TEMOA
```
Be sure the virtual enviornment is activated. If not, activate it with:
```sh
conda activate temoa
```
TEMOA can be run using the following command:
```sh
python temoa_model --config=temoa_model/config_sample
```
If the installation is correct, TEMOA should successfully solve the test model and fill the output tables of the output database with results.
___
For further assistance, refer to the official [TEMOA documentation](https://temoacloud.com/temoaproject/) or write to [matteo.nicoli@polito.it](mailto:matteo.nicoli@polito.it).