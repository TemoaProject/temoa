from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from temoa.core.model import TemoaModel


def StorageLevelVariableIndices(M: 'TemoaModel'):
    return M.storageLevelIndices_rpsdtv


def SeasonalStorageLevelVariableIndices(M: 'TemoaModel'):
    return M.seasonalStorageLevelIndices_rpstv


def SeasonalStorageConstraintIndices(M: 'TemoaModel'):
    indices = set(
        (r, p, s, d, t, v)
        for r, p, s, t, v in M.seasonalStorageLevelIndices_rpstv
        for d in M.time_of_day
    )

    return indices


def StorageConstraintIndices(M: 'TemoaModel'):
    return M.storageLevelIndices_rpsdtv
