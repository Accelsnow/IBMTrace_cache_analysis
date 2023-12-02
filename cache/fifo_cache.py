from __future__ import annotations
from typing import Tuple

from cache import BaseCache, CacheRequest
from collections import deque


class FIFOCache(BaseCache):
    queue: deque
    hiting: set

    def __init__(self, size: int, block_size: int):
        super().__init__(size, block_size)
        self.name = "FIFOCache"
        self.queue = deque(maxlen=self.num_blocks)
        self.hiting = set()

    def access(self, cache_req: CacheRequest) -> None:
        self.accesses += 1
        if cache_req.tag in self.hiting:
            self.hits += 1
        else:
            self.misses += 1
            assert len(self.queue) <= self.num_blocks
            if len(self.queue) == self.num_blocks:
                self.evict()
                assert len(self.queue) < self.num_blocks
            self.queue.append(cache_req.tag)
            self.hiting.add(cache_req.tag)

    def evict(self) -> None:
        self.evicts += 1
        self.hiting.remove(self.queue.popleft())
