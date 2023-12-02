from __future__ import annotations
from typing import Tuple
from mem_trace import AccessType


class CacheRequest:
    tag: Tuple[int, int]
    acc_type: AccessType
