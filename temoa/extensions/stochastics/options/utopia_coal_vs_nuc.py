verbose = True
force = True

dirname = 'utopia_demand'
modelpath = '../temoa_model/temoa_model.py'
dotdatpath = '../data_files/utopia-15.dat'
stochasticset = 'time_optimize'
stochastic_indices = {'Demand': 0, 'cost_invest': 1}

# CL, CA, CH = coal "[lower, average, high]" rate
# _Low, _Average, _High = demand "[low, average, high]" rate
types = (
    'CL_Low',
    'CL_Average',
    'CL_High',
    'CA_Low',
    'CA_Average',
    'CA_High',
    'CH_Low',
    'CH_Average',
    'CH_High',
)

# for this toy problem, all branches are equally likely, so 1/9
conditional_probability = dict(
    CL_Low=1.0 / 9,
    CA_Low=1.0 / 9,
    CH_Low=1.0 / 9,
    CL_Average=1.0 / 9,
    CA_Average=1.0 / 9,
    CH_Average=1.0 / 9,
    CL_High=1.0 / 9,
    CA_High=1.0 / 9,
    CH_High=1.0 / 9,
)
rates = {
    'Demand': dict(
        CL_Low=(('*,*,RH', 0.951), ('*,*,RL', 0.951), ('*,*,TX', 0.951)),
        CA_Low=(('*,*,RH', 0.951), ('*,*,RL', 0.951), ('*,*,TX', 0.951)),
        CH_Low=(('*,*,RH', 0.951), ('*,*,RL', 0.951), ('*,*,TX', 0.951)),
        CL_Average=(('*,*,RH', 1.105), ('*,*,RL', 1.105), ('*,*,TX', 1.105)),
        CA_Average=(('*,*,RH', 1.105), ('*,*,RL', 1.105), ('*,*,TX', 1.105)),
        CH_Average=(('*,*,RH', 1.105), ('*,*,RL', 1.105), ('*,*,TX', 1.105)),
        CL_High=(('*,*,RH', 1.480), ('*,*,RL', 1.480), ('*,*,TX', 1.480)),
        CA_High=(('*,*,RH', 1.480), ('*,*,RL', 1.480), ('*,*,TX', 1.480)),
        CH_High=(('*,*,RH', 1.480), ('*,*,RL', 1.480), ('*,*,TX', 1.480)),
    ),
    'cost_invest': dict(
        CL_Low=(
            ('E01,*', 1.8),
            ('E21,*', 1.2),
        ),
        CL_Average=(
            ('E01,*', 1.8),
            ('E21,*', 1.2),
        ),
        CL_High=(
            ('E01,*', 1.8),
            ('E21,*', 1.2),
        ),
        CA_Low=(
            ('E01,*', 2.0),
            ('E21,*', 0.7),
        ),
        CA_Average=(
            ('E01,*', 2.0),
            ('E21,*', 0.7),
        ),
        CA_High=(
            ('E01,*', 2.0),
            ('E21,*', 0.7),
        ),
        CH_Low=(
            ('E01,*', 2.2),
            ('E21,*', 0.2),
        ),
        CH_Average=(
            ('E01,*', 2.2),
            ('E21,*', 0.2),
        ),
        CH_High=(
            ('E01,*', 2.2),
            ('E21,*', 0.2),
        ),
    ),
}
