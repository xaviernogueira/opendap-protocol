import atoms
import constructors
import numpy as np
from typing import (
    Dict,
    Union,
    get_args,
)

AtomicTypes = Union[
    atoms.Bytes,
    atoms.Float32,
    atoms.Float64,
    atoms.Int16,
    atoms.Int32,
    atoms.UInt16,
    atoms.UInt32,
    atoms.String,
    atoms.URL,
]

ConstructorTypes = Union[
    constructors.Structure,
    constructors.Variable,
    constructors.Array,
    constructors.Grid,
]

DAPTypes = Union[
    AtomicTypes,
    ConstructorTypes,
]


NUMPY_TO_ATOMS: Dict[np.dtype, atoms.Atom] = {
    np.dtype(atom.__annotations__['value']): atom for atom in get_args(AtomicTypes)
}
