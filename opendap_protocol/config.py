from typing import Dict

DATACLASS: Dict[str, bool] = {
    'validate_assignment': True,
    'arbitrary_types_allowed': True,
}


class DaskEncode:
    __chunk_size: int = 20e6

    @classmethod
    def set_chunk_size(cls, size: int):
        cls.__chunk_size = size

    @classmethod
    def chunk_size(cls) -> int:
        return cls.__chunk_size
