import enum

from _typeshed import Incomplete
from pyomo.common.flags import building_documentation as building_documentation
from PyQt5 import uic as uic
from PyQt5.QtWidgets import QAction as QAction

supported: Incomplete
import_errors: Incomplete
available: bool
qt_package: Incomplete
QtWidgets: Incomplete
QtCore: Incomplete
QtGui: Incomplete
available = module_str

class Qt:
    class ItemDataRole(enum.Enum):
        EditRole = 1
        DisplayRole = 2
        ToolTipRole = 3
        ForegroundRole = 4

class QtCore:
    class QModelIndex: ...
    Qt = Qt

class QAbstractItemModel:
    def __init__(*args, **kwargs) -> None: ...

class QAbstractTableModel:
    def __init__(*args, **kwargs) -> None: ...

class QItemEditorCreatorBase: ...
class QItemDelegate: ...

QAbstractItemView: Incomplete
QFileDialog: Incomplete
QMainWindow: Incomplete
QMdiArea: Incomplete
QApplication: Incomplete
QTableWidgetItem: Incomplete
QStatusBar: Incomplete
QLineEdit: Incomplete
QItemEditorFactory: Incomplete
QStyledItemDelegate: Incomplete
QComboBox: Incomplete
QMessageBox: Incomplete
QColor: Incomplete
QMetaType: Incomplete

class QAbstractItemModel: ...
class QAbstractTableModel: ...
