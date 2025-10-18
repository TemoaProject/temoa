from _typeshed import Incomplete
from pyomo.contrib.parmest.examples.reactor_design.reactor_design import (
    ReactorDesignExperiment as ReactorDesignExperiment,
)

class TimeSeriesReactorDesignExperiment(ReactorDesignExperiment):
    data: Incomplete
    experiment_number: Incomplete
    data_i: Incomplete
    model: Incomplete
    def __init__(self, data, experiment_number) -> None: ...
    def finalize_model(self): ...

def main(): ...
