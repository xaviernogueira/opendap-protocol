from pydantic import (
    field_validator,
    dataclasses,
)
import urllib
import numpy as np
from enum import Enum
from typing import (
    Union,
    Dict,
    Tuple,
)
import config


def validate_ascii(v: Union[str, np.str_]) -> np.str_:
    if not isinstance(v, np.str_) and not isinstance(v, str):
        raise ValueError(f'Invalid type: {type(v)}')
    if not all(ord(c) < 128 for c in v):
        raise ValueError(f'Invalid ASCII: {v}')
    return np.str_(v)


class AtomStrings(Enum):
    BYTES = 'B'
    FLOAT32 = '>f4'
    FLOAT64 = '>f8'
    INT16 = '>i4'
    INT32 = '>i4'
    UINT16 = '>u4'
    UINT32 = '>u4'
    STRING = 'S'
    URL = 'S'


class Atom:
    @property
    def string(self):
        return getattr(AtomStrings, self.__class__.__name__.upper()).value


@dataclasses.dataclass(config=config.DATACLASS)
class Bytes(Atom):
    value: np.ubyte


@dataclasses.dataclass(config=config.DATACLASS)
class Float32(Atom):
    value: np.float32


@dataclasses.dataclass(config=config.DATACLASS)
class Float64(Atom):
    value: np.float64


@dataclasses.dataclass(config=config.DATACLASS)
class Int16(Atom):
    value: np.int16


@dataclasses.dataclass(config=config.DATACLASS)
class Int32(Atom):
    value: np.int32


@dataclasses.dataclass(config=config.DATACLASS)
class UInt16(Atom):
    value: np.uint16


@dataclasses.dataclass(config=config.DATACLASS)
class UInt32(Atom):
    value: np.uint32


@dataclasses.dataclass(config=config.DATACLASS)
class String(Atom):
    value: np.str_

    @field_validator('value', mode='before')
    def validate_string(cls, v: Union[str, np.str_]) -> np.str_:
        return validate_ascii(v)


@dataclasses.dataclass(config=config.DATACLASS)
class URL(Atom):
    value: np.str_

    @field_validator('value', mode='before')
    def validate_url(v: Union[str, np.str_]) -> np.str_:
        v: np.str_ = validate_ascii(v)
        try:
            url = urllib.parse.urlparse(v)
            if not all([url.scheme, url.netloc]):
                raise ValueError
        except ValueError:
            raise ValueError(f'Invalid URL: {v}')
        return v
