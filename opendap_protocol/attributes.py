from pydantic import dataclasses
from typing import (
    Union,
    List,
)
from shared import DATACLASS_CONFIG_DICT as CONFIG_DICT
from constructors import Structure
from atoms import (
    Atom,
)

AttributeTypes: Union[
    Atom,
    Structure,
]


@dataclasses.dataclass(config=CONFIG_DICT)
class Attribute:
    value: AttributeTypes


@dataclasses.dataclass(config=CONFIG_DICT)
class AttributeStructure:
    values: List[Attribute]
