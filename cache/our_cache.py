from __future__ import annotations
from typing import Dict, Tuple, Union, Deque
from cache import BaseCache, CacheRequest
from collections import deque
import bisect


class SortedList:
    def __init__(self):
        self.items = []

    def insert(self, num):
        bisect.insort(self.items, num)


class OurCache(BaseCache):
    cache_dict: Dict[Tuple[int, int], int]
    cache_evict_dict: Dict[int, Deque[Tuple[int, int]]]
    # cache_evict_queue: deque
    recent_evict_dict: dict
    recent_evict_queue: deque
    evict_blocks: int
    cache_blocks: int

    def __init__(self, size: int, block_size: int, evict_blocks: Union[int, float]):
        super().__init__(size, block_size)
        self.name = "OurCache"
        if evict_blocks < 1:
            self.evict_blocks = int(evict_blocks * self.num_blocks)
        elif evict_blocks < self.num_blocks:
            self.evict_blocks = evict_blocks
        else:
            print(f"WARNING: our cache evict block {evict_blocks} is larger than total cache blocks {self.num_blocks}! "
                  f"Fallback to 1000.")
            self.evict_blocks = 1000
        self.cache_blocks = self.num_blocks - self.evict_blocks
        self.cache_dict = {}
        self.cache_evict_dict = {}
        for i in range(0, 256):
            self.cache_evict_dict[i] = deque(maxlen=self.evict_blocks)
        self.recent_evict_dict = {}
        self.recent_evict_queue = deque(maxlen=self.evict_blocks)
        self.description += f"{self.evict_blocks} ev_blks, {self.cache_blocks} c_blks"

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

            assert len(self.cache_dict) < self.cache_blocks
            self.cache_dict[cache_req.tag] = evict_weight
            assert len(self.cache_evict_dict[evict_weight]) < self.cache_blocks
            self.cache_evict_dict[evict_weight].append(cache_req.tag)

    def our_evict(self) -> None:
        self.evicts += 1
        target_weight = 0
        while target_weight <= 255 and len(self.cache_evict_dict[target_weight]) == 0:
            target_weight += 1
        assert target_weight <= 255
        target_tag = self.cache_evict_dict[target_weight].popleft()
        assert self.cache_dict.pop(target_tag) == target_weight
        # assert target_tag not in self.recent_evict_dict

        if len(self.recent_evict_dict) == self.evict_blocks:
            self.recent_evict_dict.pop(self.recent_evict_queue.popleft())
        assert len(self.recent_evict_dict) < self.evict_blocks
        if target_tag not in self.recent_evict_dict:
            self.recent_evict_queue.append(target_tag)

        self.recent_evict_dict[target_tag] = target_weight
