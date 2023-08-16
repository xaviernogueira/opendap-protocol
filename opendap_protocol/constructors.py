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
from shared import DATACLASS_CONFIG_DICT as CONFIG_DICT


@runtime_checkable
class Structure(Protocol):
    variables: Any

    @property
    def shape(self):
        ...


@dataclasses.dataclass(config=CONFIG_DICT)
class Variable:
    ...


@dataclasses.dataclass(config=CONFIG_DICT)
class Array:
    ...


@dataclasses.dataclass(config=CONFIG_DICT)
class Grid:
    value: np.ndarray

    @property
    def shape(self):
        return self.value.shape

    @field_validator('value', mode='before')
    def check_grid_dtype(self, value):
        """Check that grid is of an atomic type"""
        ...


@dataclasses.dataclass(config=CONFIG_DICT)
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
