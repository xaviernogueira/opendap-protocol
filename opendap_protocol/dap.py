from protocols import DAP
from shared import (
    AtomicTypes,
    ConstructorTypes,
    DAPTypes,
)
from typing import (
    Dict,
    Union,
    Generator,
)

PROTOCOL_MAPPER: Dict[str, DAP] = {
    'Grid': None,
    'Sequence': None,
    'Structure': None,
    'Array': None,
    'Variable': None,
    # TODO: add this
}


def dds(input: DAPTypes) -> Generator:
    ...


def das(input: DAPTypes) -> Generator:
    ...


def dods(input: DAPTypes) -> Generator:
    ...
