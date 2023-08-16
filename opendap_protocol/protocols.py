from typing import (
    Protocol,
    Generator,
)


class DAP(Protocol):

    @staticmethod
    def dds() -> Generator:
        ...

    @staticmethod
    def das() -> Generator:
        ...

    @staticmethod
    def dods() -> Generator:
        ...
