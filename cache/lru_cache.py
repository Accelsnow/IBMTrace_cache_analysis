from cache import BaseCache, CacheRequest
from collections import OrderedDict


class LRUCache(BaseCache):
    entries: OrderedDict

    def __init__(self, size: int, block_size: int):
        super().__init__(size, block_size)
        self.name = "LRUCache"
        self.entries = OrderedDict()

    def access(self, cache_request: CacheRequest) -> None:
        self.accesses += 1
        if cache_request.tag in self.entries:
            self.hits += 1
            self.entries.move_to_end(cache_request.tag)
        else:
            self.misses += 1
            assert len(self.entries) <= self.num_blocks
            if len(self.entries) == self.num_blocks:
                self.evict()
                assert len(self.entries) < self.num_blocks
            self.entries[cache_request.tag] = 1

    def evict(self) -> None:
        self.evicts += 1
        self.entries.popitem(last=False)
