from pydantic import (
    field_validator,
    dataclasses,
)
import urllib
import numpy as np
from typing import (
    Dict,
    Union,
)

CONFIG_DICT: Dict[str, bool] = {
    'validate_assignment': True,
    'arbitrary_types_allowed': True,
}


def validate_ascii(v: Union[str, np.str_]) -> np.str_:
    if not all(ord(c) < 128 for c in v):
        raise ValueError(f'Invalid ASCII: {v}')
    return np.str_(v)


@dataclasses.dataclass(config=CONFIG_DICT)
class Bytes:
    value: bytes


@dataclasses.dataclass(config=CONFIG_DICT)
class Float32:
    value: np.float32


@dataclasses.dataclass(config=CONFIG_DICT)
class Float64:
    value: np.float64


@dataclasses.dataclass(config=CONFIG_DICT)
class Int16:
    value: np.int16


@dataclasses.dataclass(config=CONFIG_DICT)
class Int32:
    value: np.int32


@dataclasses.dataclass(config=CONFIG_DICT)
class UInt16:
    value: np.uint16


@dataclasses.dataclass(config=CONFIG_DICT)
class UInt32:
    value: np.uint32

    @field_validator('value', mode='before')
    def validate(cls, v):
        return validate_ascii(v)


@dataclasses.dataclass(config=CONFIG_DICT)
class String:
    value: np.str_

    @field_validator('value', mode='before')
    def validate_string(cls, v: Union[str, np.str_]) -> np.str_:
        return validate_ascii(v)


@dataclasses.dataclass(config=CONFIG_DICT)
class URL:
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
