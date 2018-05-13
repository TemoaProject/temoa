from pyomo.environ import *
from pyomo.core import Objective, Var, Constraint
from pyomo.opt import SolverFactory
import sys, os
from matplotlib import pyplot as plt
import numpy as np
from IPython import embed as IP
from temoa_model import temoa_create_model
from temoa_initialize import DemandConstraintErrorCheck
from temoa_rules import PeriodCost_rule
from pformat_results import pformat_results
from temoa_config import db_2_dat
from temoa_config import TemoaConfig
import time

import os

t0=time.time()
options=TemoaConfig()
options.output=os.getcwd()+'/db_io/dbs/temoa_utopia.db'
options.keepPyomoLP=False
options.dot_dat=[os.getcwd()+'/data_files/utopia_ELC.dat']
options.path_to_db_io=os.getcwd()+'/db_io'
options.scenario='Robust'
options.saveEXCEL=True
options.saveTEXTFILE=True
options.mga_weight=[]





def pf_result(dat,dat1):
    M = temoa_create_model()
    M.num_scenarios                = Param()
    M.scenario                     = Set(ordered=True, rule=lambda M: range(1, value(M.num_scenarios) + 1))
    M.EmissionLimitMultiplier      = Param(M.commodity_emissions,M.scenario)
    M.phi                          = Param()

    data1 = DataPortal(model = M)
    data1.load(filename=dat)
    data1.load(filename=dat1)
    #print( "Creating model instance...")
    #instance = M.create_instance(data1)
    Cost = []

    SCENARIOS=[1,2,3,4]

    #sorted(instance.scenario.keys())
    
    for scenario in SCENARIOS:
        M.del_component('EmissionLimitConstraint')

        def EmissionLimit_Constraint ( M, p, e ):

            if e==M.EmissionLimitMultiplier.keys()[0][0]: 
                periods=[i[0] for i in M.EmissionLimit.keys() if i[1]==e]
                periods.sort()
                emission_limit=M.EmissionLimit[p, e]-((p-periods[0])/(periods[-1]-periods[0]))*(M.EmissionLimit[periods[0], e]-value(M.EmissionLimitMultiplier[e,scenario])*M.EmissionLimit[periods[0], e])
            else:
                emission_limit=M.EmissionLimit[p, e]
            
            
            actual_emissions = sum(
                M.V_FlowOut[p, S_s, S_d, S_i, S_t, S_v, S_o]
              * M.EmissionActivity[e, S_i, S_t, S_v, S_o]
        
              for tmp_e, S_i, S_t, S_v, S_o in M.EmissionActivity.sparse_iterkeys()
              if tmp_e == e
              if M.ValidActivity( p, S_t, S_v )
              for S_s in M.time_season
              for S_d in M.time_of_day
            )
        
            if int is type( actual_emissions ):
                msg = ("Warning: No technology produces emission '%s', though limit was "
                  'specified as %s.\n')
                SE.write( msg % (e, emission_limit) )
                return Constraint.Skip
        
            expr = (actual_emissions <= emission_limit)
            return expr
        
        M.EmissionLimitConstraint = Constraint( M.EmissionLimitConstraint_pe, rule=EmissionLimit_Constraint)
        
        
        print( "Creating instance of scenario", scenario )
        instance = M.create_instance(data1)
        print (time.time()-t0)


        optimizer = SolverFactory('cplex')
        print( "Solving scenario" , scenario )
        results = optimizer.solve(instance)
        instance.solutions.store_to(results)
        print (time.time()-t0)
        Cost.append(value(instance.TotalCost))


    #scenario_cost = open("ScenarioCost.dat", "w") #create a new file
    #print >> scenario_cost, """\
    #data;
    #
    #param: scenarioCost  :=
    #    # scenario        #cost
    #"""
    #for scenario in sorted(instance.scenario.keys()):
    #    print >> scenario_cost, "    %10g    %10s    " % \
    #            (scenario, Cost[scenario - 1])
    #
    #print >> scenario_cost, "    ;\n"
    #scenario_cost.close()
    return Cost


def temoa_robust(dat, dat1):
    M = temoa_create_model()
    def Robust_rule ( M ):
        #regret = sum(M.regret[scenario] for scenario in M.scenario)
        risk = value(M.phi) * (sum((M.z[p,s,d,dem,scenario] * M.z[p,s,d,dem,scenario]) for p,s,d,dem,scenario in M.DemandConstraint))
        cost = sum( PeriodCost_rule(M, p) for p in M.time_optimize )

        return (cost + risk)

    def Demand_Constraint ( M, p, s, d, dem, scenario ):

        supply = sum(
          M.V_FlowOut[p, s, d, S_i, S_t, S_v, dem]
    
          for S_t, S_v in M.helper_commodityUStreamProcess[ p, dem ]
          for S_i in M.helper_ProcessInputsByOutput[ p, S_t, S_v, dem ]
        ) 
    
        DemandConstraintErrorCheck( supply, p, s, d, dem )
    
        expr = (supply + M.z[p, s, d, dem, scenario] == M.Demand[p, dem] * M.DemandSpecificDistribution[s, d, dem] )
    
        return expr

    #def regret_Constraint(M, scenario):
    #    expr = (M.regret[scenario] == sum( PeriodCost_rule(M, p) for p in M.time_optimize ) - value(M.scenarioCost[scenario]))
    #    return expr

    def real_obj(M): #STOCH ELASTIC
        a = sum( PeriodCost_rule(M, p)  for p in M.time_optimize )
        expr = (a >= 0)
        return expr

    def EmissionLimit_Constraint ( M, p, e, scenario ):
        
        if e==M.EmissionLimitMultiplier.keys()[0][0]: 
            periods=[i[0] for i in M.EmissionLimit.keys() if i[1]==e]
            periods.sort()
            emission_limit=M.EmissionLimit[p, e]-((p-periods[0])/(periods[-1]-periods[0]))*(M.EmissionLimit[periods[0], e]-value(M.EmissionLimitMultiplier[e,scenario])*M.EmissionLimit[periods[0], e])
        else:
            emission_limit=M.EmissionLimit[p, e]       

    
        actual_emissions = sum(
            M.V_FlowOut[p, S_s, S_d, S_i, S_t, S_v, S_o]
          * M.EmissionActivity[e, S_i, S_t, S_v, S_o]
    
          for tmp_e, S_i, S_t, S_v, S_o in M.EmissionActivity.sparse_iterkeys()
          if tmp_e == e
          if M.ValidActivity( p, S_t, S_v )
          for S_s in M.time_season
          for S_d in M.time_of_day
        )
    
        if int is type( actual_emissions ):
            msg = ("Warning: No technology produces emission '%s', though limit was "
              'specified as %s.\n')
            SE.write( msg % (e, emission_limit) )
            return Constraint.Skip
    
        expr = (actual_emissions <= emission_limit)
        return expr


        
    M.del_component('TotalCost')
    M.del_component('DemandConstraint')
    M.del_component('M.DemandActivityConstraint_psdtv_dem_s0d0')
    M.del_component('DemandActivityConstraint')
    M.del_component('EmissionLimitConstraint')
    # Efficiency: all the parameters
    M.num_scenarios                = Param()
    M.scenario                     = Set(ordered=True, rule=lambda M: range(1, value(M.num_scenarios) + 1))
    M.EmissionLimitMultiplier      = Param(M.commodity_emissions,M.scenario)
    M.z                            = Var(M.time_optimize, M.time_season, M.time_of_day, M.commodity_demand, M.scenario)
    #M.regret                       = Var(M.scenario)
    M.phi                          = Param()
    #M.scenarioCost                 = Param(M.scenario)
    
    M.TotalCost                    = Constraint(rule=real_obj)
    M.DemandConstraint             = Constraint( M.time_optimize, M.time_season, M.time_of_day, M.commodity_demand, M.scenario, rule=Demand_Constraint )
    #M.regret_Constraint            = Constraint(M.scenario, rule=regret_Constraint)
    M.EmissionLimitConstraint      = Constraint( M.EmissionLimitConstraint_pe, M.scenario, rule=EmissionLimit_Constraint)

    M.Robust = Objective(rule=Robust_rule, sense=minimize)

    data1 = DataPortal(model = M)
    data1.load(filename=dat)
    data1.load(filename=dat1)
    #data1.load(filename=dat2)
    print( "Creating instance of robust model.. ")
    instance = M.create_instance(data1)
    print (time.time()-t0)


    optimizer = SolverFactory('cplex')
    print( "Solving  robust model.. ")
    results = optimizer.solve(instance)
    instance.solutions.store_to(results)
    print (time.time()-t0)

    return instance , results





def Robust_run():
    model = temoa_create_model()
    db=os.getcwd()+'/db_io/dbs/temoa_utopia_New.db'
    dat = os.getcwd()+'/data_files/utopia_ELC_REN.dat'
    #db_2_dat(db,dat,options)
    dat1 = os.getcwd()+'/data_files/scenarios_emission.dat'
    #scenario_cost = pf_result(dat, dat1)
    #dat2 = '/raid60/home/heshrag/temoa-energysystem/ScenarioCost.dat'
    instance , results = temoa_robust(dat, dat1)

    print( "Writing solution to database.. ")
    pformat_results( instance, results, options )
    print (time.time()-t0)
 

    import csv
    import numpy
    with open('Zees_phi='+str(value(instance.phi))+'.csv', 'w') as f:
        writer = csv.writer(f, delimiter=',')
        for j in instance.z.iterkeys():
            writer.writerow(numpy.append(j,value(instance.z[j])))
    



if __name__ == "__main__":
    Robust_run()
    sys.stdout.write('\a\a')
    sys.stdout.flush()