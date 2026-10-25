from pyomo.contrib.mpc.examples.cstr.model import create_instance as create_instance

def get_input_sequence(): ...
def run_cstr_openloop(
    inputs,
    model_horizon: float = 1.0,
    ntfe: int = 10,
    simulation_steps: int = 15,
    tee: bool = False,
): ...
def main() -> None: ...
