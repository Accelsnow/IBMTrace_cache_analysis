from cache import BaseCache
from mem_trace import Trace
from collections import deque


class FIFOCache(BaseCache):
    queue: deque

    def __init__(self, size: int, block_size: int):
        super().__init__(size, block_size)
        self.name = "FIFOCache"
        self.queue = deque(maxlen=self.num_blocks)

    def access(self, trace: Trace):
        self.accesses += 1
        if trace.tag in self.queue:
            self.hits += 1
        else:
            self.misses += 1
            if len(self.queue) == self.num_blocks:
                self.evict()
            self.queue.append(trace.block)
