from dataclasses import dataclass


@dataclass(frozen=True)
class Yard:
    id: str
    width: int
    height: int
    crane_capacity: int = 1


@dataclass(frozen=True)
class Block:
    id: str
    width: int
    height: int
    ready_day: int
    due_day: int
    priority: int = 1


@dataclass(frozen=True)
class Placement:
    block_id: str
    yard_id: str
    x: int
    y: int
    width: int
    height: int
    start_day: int
    finish_day: int
    rotated: bool = False

    @property
    def area(self) -> int:
        return self.width * self.height

