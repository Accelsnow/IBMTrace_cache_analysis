from __future__ import annotations
from typing import Tuple
from enum import Enum


class AccessType(Enum):
    INVALID = -1,
    READ = 0,
    WRITE = 1,
    DELETE = 2,


class CacheRequest:
    tag: Tuple[int, int]
    acc_type: AccessType

    def __init__(self, tag: Tuple[int, int], acc_type: AccessType):
        self.tag = tag
        self.acc_type = acc_type
