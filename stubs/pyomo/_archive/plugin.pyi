from pyomo.core.base.component import ModelComponentFactory as ModelComponentFactory
from pyomo.core.base.transformation import Transformation as Transformation
from pyomo.core.base.transformation import TransformationData as TransformationData
from pyomo.core.base.transformation import TransformationFactory as TransformationFactory
from pyomo.core.base.transformation import TransformationInfo as TransformationInfo
from pyomo.core.base.transformation import TransformationTimer as TransformationTimer
from pyomo.scripting.interface import DeprecatedInterface as DeprecatedInterface
from pyomo.scripting.interface import ExtensionPoint as ExtensionPoint
from pyomo.scripting.interface import Interface as Interface
from pyomo.scripting.interface import IPyomoPresolveAction as IPyomoPresolveAction
from pyomo.scripting.interface import IPyomoPresolver as IPyomoPresolver
from pyomo.scripting.interface import IPyomoScriptCreateDataPortal as IPyomoScriptCreateDataPortal
from pyomo.scripting.interface import IPyomoScriptCreateModel as IPyomoScriptCreateModel
from pyomo.scripting.interface import IPyomoScriptModifyInstance as IPyomoScriptModifyInstance
from pyomo.scripting.interface import IPyomoScriptPostprocess as IPyomoScriptPostprocess
from pyomo.scripting.interface import IPyomoScriptPreprocess as IPyomoScriptPreprocess
from pyomo.scripting.interface import IPyomoScriptPrintInstance as IPyomoScriptPrintInstance
from pyomo.scripting.interface import IPyomoScriptPrintModel as IPyomoScriptPrintModel
from pyomo.scripting.interface import IPyomoScriptPrintResults as IPyomoScriptPrintResults
from pyomo.scripting.interface import IPyomoScriptSaveInstance as IPyomoScriptSaveInstance
from pyomo.scripting.interface import IPyomoScriptSaveResults as IPyomoScriptSaveResults
from pyomo.scripting.interface import Plugin as Plugin
from pyomo.scripting.interface import implements as implements
from pyomo.scripting.interface import pyomo_callback as pyomo_callback

class IPyomoExpression(DeprecatedInterface):
    def type(self) -> None: ...
    def create(self, args) -> None: ...

class IParamRepresentation(DeprecatedInterface): ...
