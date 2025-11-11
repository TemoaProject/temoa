verbose = True
force = True

dirname = 'temoa_island'
modelpath = '../temoa_model/temoa_model.py'
dotdatpath = '../data_files/iew2012.dat'
stochasticset = 'time_optimize'
stochastic_points = (2020, 2025, 2030, 2035)
stochastic_indices = {'Demand': 0, 'cost_variable': 0}
types = (
    'DemD_NatD_OilD',
    'DemD_NatD_OilU',
    'DemD_NatU_OilD',
    'DemD_NatU_OilU',
    'DemU_NatD_OilD',
    'DemU_NatD_OilU',
    'DemU_NatU_OilD',
    'DemU_NatU_OilU',
)
conditional_probability = dict(
    DemD_NatD_OilD=0.0952,
    DemD_NatD_OilU=0.0238,
    DemD_NatU_OilD=0.0952,
    DemD_NatU_OilU=0.1429,
    DemU_NatD_OilD=0.1429,
    DemU_NatD_OilU=0.1667,
    DemU_NatU_OilD=0.0952,
    DemU_NatU_OilU=0.2381,
)

rates = {
    'Demand': dict(
        DemD_NatD_OilD=(
            ('*,*,r_cooling', 0.95937),
            ('*,*,r_heating', 0.95937),
            ('*,*,r_lighting', 0.95937),
            ('*,*,r_wheating', 0.95937),
        ),
        DemD_NatD_OilU=(
            ('*,*,r_cooling', 0.78503),
            ('*,*,r_heating', 0.78503),
            ('*,*,r_lighting', 0.78503),
            ('*,*,r_wheating', 0.78503),
        ),
        DemD_NatU_OilD=(
            ('*,*,r_cooling', 0.92841),
            ('*,*,r_heating', 0.92841),
            ('*,*,r_lighting', 0.92841),
            ('*,*,r_wheating', 0.92841),
        ),
        DemD_NatU_OilU=(
            ('*,*,r_cooling', 0.90791),
            ('*,*,r_heating', 0.90791),
            ('*,*,r_lighting', 0.90791),
            ('*,*,r_wheating', 0.90791),
        ),
        DemU_NatD_OilD=(
            ('*,*,r_cooling', 1.18282),
            ('*,*,r_heating', 1.18282),
            ('*,*,r_lighting', 1.18282),
            ('*,*,r_wheating', 1.18282),
        ),
        DemU_NatD_OilU=(
            ('*,*,r_cooling', 1.20957),
            ('*,*,r_heating', 1.20957),
            ('*,*,r_lighting', 1.20957),
            ('*,*,r_wheating', 1.20957),
        ),
        DemU_NatU_OilD=(
            ('*,*,r_cooling', 1.20281),
            ('*,*,r_heating', 1.20281),
            ('*,*,r_lighting', 1.20281),
            ('*,*,r_wheating', 1.20281),
        ),
        DemU_NatU_OilU=(
            ('*,*,r_cooling', 1.12236),
            ('*,*,r_heating', 1.12236),
            ('*,*,r_lighting', 1.12236),
            ('*,*,r_wheating', 1.12236),
        ),
    ),
    'cost_variable': dict(
        DemD_NatD_OilD=(('imp_natgas,*', 0.73351), ('imp_oil,*', 0.15309)),
        DemD_NatD_OilU=(('imp_natgas,*', 0.95164), ('imp_oil,*', 2.67004)),
        DemD_NatU_OilD=(('imp_natgas,*', 1.68052), ('imp_oil,*', 0.55464)),
        DemD_NatU_OilU=(('imp_natgas,*', 1.40218), ('imp_oil,*', 4.45265)),
        DemU_NatD_OilD=(('imp_natgas,*', 0.74707), ('imp_oil,*', 0.62440)),
        DemU_NatD_OilU=(('imp_natgas,*', 0.75098), ('imp_oil,*', 2.11862)),
        DemU_NatU_OilD=(('imp_natgas,*', 1.37597), ('imp_oil,*', 0.66387)),
        DemU_NatU_OilU=(('imp_natgas,*', 1.45544), ('imp_oil,*', 2.34730)),
    ),
}
