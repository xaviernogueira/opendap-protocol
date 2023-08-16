from pydantic import dataclasses
from typing import (
    Union,
    List,
)
import config
from constructors import Structure
from atoms import (
    Atom,
)

AttributeTypes: Union[
    Atom,
    Structure,
]


@dataclasses.dataclass(config=config.DATACLASS)
class Attribute:
    value: AttributeTypes


@dataclasses.dataclass(config=config.DATACLASS)
class AttributeStructure:
    values: List[Attribute]
