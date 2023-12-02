from __future__ import annotations

from cache import BaseCache, CacheRequest
from collections import deque
import bisect

class SortedList:
    def __init__(self):
        self.items = []

    def insert(self, num):
        bisect.insort(self.items, num)


class OurCache(BaseCache):
    cache_dict: dict
    cache_evict_queue: deque
    recent_evict_dict: dict
    recent_evict_queue: deque
    evict_blocks: int
    cache_blocks: int

    def __init__(self, size: int, block_size: int):
        super().__init__(size, block_size)
        self.name = "OurCache"
        self.evict_blocks = self.num_blocks // 10
        self.cache_blocks = self.num_blocks - self.evict_blocks
        self.cache_dict = {}
        self.cache_evict_queue = deque(maxlen=self.cache_blocks)
        self.recent_evict_dict = {}
        self.recent_evict_queue = deque(maxlen=self.evict_blocks)

    def access(self, cache_req: CacheRequest) -> None:
        self.accesses += 1
        if cache_req.tag in self.cache_dict:
            self.hits += 1
        else:
            self.misses += 1

            if cache_req.tag in self.recent_evict_dict:
                evict_weight = self.recent_evict_dict[cache_req.tag] + 1
                # self.recent_evict_queue.remove(cache_req.tag)
                # self.recent_evict_dict.pop(cache_req.tag)
            else:
                evict_weight = 0

            if len(self.cache_dict) == self.cache_blocks:
                self.our_evict()

            assert len(self.cache_dict) < self.num_blocks
            self.cache_dict[cache_req.tag] = evict_weight

            evict_queue_entry = cache_req.tag[0], cache_req.tag[1], self.cache_dict[cache_req.tag]
            bisect.insort(self.cache_evict_queue, evict_queue_entry, key=lambda x: x[2])

    def our_evict(self) -> None:
        self.evicts += 1
        target = self.cache_evict_queue.popleft()
        tag = target[0], target[1]
        assert self.cache_dict.pop(tag) == target[2]
        assert tag not in self.recent_evict_dict

        if len(self.recent_evict_dict) == self.evict_blocks:
            self.recent_evict_dict.pop(self.recent_evict_queue.popleft())
        assert len(self.recent_evict_dict) < self.evict_blocks
        self.recent_evict_dict[tag] = target[2]
        self.recent_evict_queue.append(tag)


