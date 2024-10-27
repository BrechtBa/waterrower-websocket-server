from dataclasses import dataclass
from typing import Union, Callable


@dataclass
class Event:
    event_type: str
    value: Union[float, int, str, None]
    raw: str
    timestamp: int


class IRower:
    def register_callback(self, callback: Callable[[Event], None]) -> None:
        raise NotImplementedError
