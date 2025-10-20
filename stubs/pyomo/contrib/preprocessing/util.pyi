from pyomo.common.log import LoggingIntercept as LoggingIntercept

class SuppressConstantObjectiveWarning(LoggingIntercept):
    def __init__(self) -> None: ...
