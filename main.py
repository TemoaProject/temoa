"""
new entry point for running the model.
"""
# Written by:  J. F. Hyink
# jeff@westernspark.us
# https://westernspark.us

# Created on:  7/18/23


from temoa.temoa_model.temoa_model import temoa_create_model
from temoa.temoa_model.temoa_run import TemoaSolver

def runModelUI(config_filename):
    """This function launches the model run from the Temoa GUI"""
    raise NotImplementedError
    solver = TemoaSolver(model, config_filename)
    for k in solver.createAndSolve():
        yield k
        # yield " " * 1024


def runModel():
    """This function launches the model run, and is invoked when called from
    __main__.py"""

    dummy = ""  # If calling from command line, send empty string
    model = temoa_create_model()
    solver = TemoaSolver(model, dummy)
    for k in solver.createAndSolve():
        pass

if __name__ == '__main__':
    runModel()