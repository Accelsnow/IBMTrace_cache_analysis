from __future__ import annotations

from cache import BaseCache, CacheRequest
from collections import deque


class FIFOCache(BaseCache):
    queue: deque
    entry_set: set

    def __init__(self, size: int, block_size: int, filename: str):
        super().__init__(size, block_size, filename)
        self.name = "FIFOCache"
        self.queue = deque(maxlen=self.num_blocks)
        self.entry_set = set()

    def access(self, cache_req: CacheRequest) -> None:
        self.accesses += 1
        if cache_req.tag in self.entry_set:
            self.hits += 1
        else:
            self.misses += 1
            assert len(self.queue) <= self.num_blocks
            if len(self.queue) == self.num_blocks:
                self.evict()
                assert len(self.queue) < self.num_blocks
            self.queue.append(cache_req.tag)
            self.entry_set.add(cache_req.tag)

    def evict(self) -> None:
        self.evicts += 1
        self.entry_set.remove(self.queue.popleft())
