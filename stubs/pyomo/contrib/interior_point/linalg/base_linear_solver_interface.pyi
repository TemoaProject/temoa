from abc import ABCMeta, abstractmethod

from pyomo.contrib.pynumero.linalg.base import (
    DirectLinearSolverInterface as DirectLinearSolverInterface,
)

class IPLinearSolverInterface(DirectLinearSolverInterface, metaclass=ABCMeta):
    @classmethod
    def getLoggerName(cls): ...
    @classmethod
    def getLogger(cls): ...
    def increase_memory_allocation(self, factor) -> None: ...
    @abstractmethod
    def get_inertia(self): ...
