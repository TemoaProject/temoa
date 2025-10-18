import enum

class ProblemFormat(str, enum.Enum):
    pyomo = 'pyomo'
    cpxlp = 'cpxlp'
    nl = 'nl'
    mps = 'mps'
    mod = 'mod'
    lpxlp = 'lpxlp'
    osil = 'osil'
    bar = 'bar'
    gams = 'gams'

class ResultsFormat(str, enum.Enum):
    osrl = 'osrl'
    results = 'results'
    sol = 'sol'
    soln = 'soln'
    yaml = 'yaml'
    json = 'json'

def guess_format(filename): ...
