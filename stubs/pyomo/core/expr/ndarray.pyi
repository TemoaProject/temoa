from pyomo.common.dependencies import numpy_available as numpy_available

class NumericNDArray:
    def __array_ufunc__(self, ufunc, method, *inputs, **kwargs): ...
