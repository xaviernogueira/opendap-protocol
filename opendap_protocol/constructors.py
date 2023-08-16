from pydantic import (
    dataclasses,
    field_validator,
)
import numpy as np
from typing import (
    List,
    Protocol,
    Any,
    runtime_checkable
)
from atoms import Atom
import config
from shared import (
    ATOMIC_TYPES,
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
    value: np.ndarray

    @property
    def shape(self):
        return self.value.shape

    @property
    def atomic_type(self):
        return NUMPY_TO_ATOMS[self.value.dtype]

    @field_validator('value', mode='before')
    def check_grid_dtype(self, value: np.ndarray) -> np.ndarray:
        """Check that grid is of an atomic type"""
        if not isinstance(value, np.ndarray):
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
    def check_sequence(self, value):
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
    Grid(np.array([1, 2, 3]))
