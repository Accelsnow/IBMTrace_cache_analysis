from __future__ import annotations

from typing import Tuple
from cache import AccessType


class Trace:
    tag: Tuple[int, int]
    tot_size: int
    acc_start: int
    acc_end: int
    acc_type: AccessType

    def acc_size(self):
        return self.acc_end - self.acc_start + 1

    def __str__(self):
        return f"{self.tag} {self.acc_type}, {self.tot_size} : [{self.acc_start}, {self.acc_end}]"
