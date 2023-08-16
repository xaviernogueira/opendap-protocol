import atoms
import numpy as np
from typing import (
    Dict,
    Tuple,
)

DATACLASS_CONFIG_DICT: Dict[str, bool] = {
    'validate_assignment': True,
    'arbitrary_types_allowed': True,
}

ATOMIC_TYPES = Tuple[atoms.Atom] = (
    atoms.Bytes,
    atoms.Float32,
    atoms.Float64,
    atoms.Int16,
    atoms.Int32,
    atoms.UInt16,
    atoms.UInt32,
    atoms.String,
    atoms.URL,
)

NUMPY_TO_ATOMS: Dict[np.dtype, atoms.Atom] = {
    np.dtype(atom.__annotations__['value']): atom for atom in ATOMIC_TYPES
}
