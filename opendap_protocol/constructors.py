from pydantic import (
    dataclasses,
    field_validator,
)
import numpy as np
import dask.array as da
from typing import (
    List,
    Protocol,
    Any,
    Union,
    runtime_checkable,
)
import config
from shared import (
    NUMPY_TO_ATOMS,
)


@runtime_checkable
class Structure(Protocol):
    variables: Any

    @property
    def shape(self):
        ...


@dataclasses.dataclass(config=config.DATACLASS)
class Variable:
    ...


@dataclasses.dataclass(config=config.DATACLASS)
class Array:
    ...


@dataclasses.dataclass(config=config.DATACLASS)
class Grid:
    value: Union[np.ndarray, da.Array]

    @property
    def shape(self):
        return self.value.shape

    @property
    def atomic_type(self):
        return NUMPY_TO_ATOMS[self.value.dtype]

    @field_validator('value', mode='before')
    def check_grid_dtype(cls, value: np.ndarray) -> np.ndarray:
        """Check that grid is of an atomic type"""
        if not isinstance(value, np.ndarray) and not isinstance(value, da.Array):
            raise ValueError('Grid must be a numpy array')
        if value.dtype not in NUMPY_TO_ATOMS.keys():
            raise ValueError(
                f'Grid must be of an atomic type: {NUMPY_TO_ATOMS.keys()}'
            )
        return value


@dataclasses.dataclass(config=config.DATACLASS)
class Sequence:
    value: List[Structure]

    @field_validator('value', mode='before')
    def check_sequence(cls, value):
        length: int = 0

        for i, struct in enumerate(value):
            if not isinstance(struct, Structure):
                raise ValueError('All elements in sequence must be structures')
            if i == 0:
                length = len(struct.value)
            elif len(struct.value) != len(length):
                raise ValueError(
                    'All structures in sequence must have the same length')
        return value


if __name__ == '__main__':
    g = Grid(np.array([1, 2, 3]))
    print(g)
