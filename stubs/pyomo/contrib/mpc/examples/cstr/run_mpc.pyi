from pyomo.contrib.mpc.examples.cstr.model import create_instance as create_instance

def get_steady_state_data(target, tee: bool = False): ...
def run_cstr_mpc(
    initial_data,
    setpoint_data,
    samples_per_controller_horizon: int = 5,
    sample_time: float = 2.0,
    ntfe_per_sample_controller: int = 2,
    ntfe_plant: int = 5,
    simulation_steps: int = 5,
    tee: bool = False,
): ...
def main() -> None: ...
