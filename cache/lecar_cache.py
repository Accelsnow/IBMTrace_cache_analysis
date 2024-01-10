import random
from cache import BaseCache, CacheRequest
from collections import OrderedDict

class LeCaRCache(BaseCache):
    def __init__(self, size: int, block_size: int, filename: str):
        super().__init__(size, block_size, filename)
        self.name = "LeCaRCache"
        self.Cache = OrderedDict()  # Shared cache space
        # self.LRU = OrderedDict()  # LRU order
        # self.FIFO = OrderedDict()  # FIFO order
        self.HLRU = OrderedDict()  # History for LRU
        self.HFIFO = OrderedDict()  # History for FIFO
        self.wLRU = 0.5  # Initial weight for LRU
        self.wFIFO = 0.5  # Initial weight for FIFO
        self.lamb = 0.1  # Learning rate

    def _update_weight(self, q, lamb, d):
        # Update weights based on access pattern
        if q in self.HLRU:
            self.wLRU = self.wLRU + lamb * (1 - self.wLRU)
            self.wFIFO = 1 - self.wLRU
            del self.HLRU[q]
        elif q in self.HFIFO:
            self.wFIFO = self.wFIFO + lamb * (1 - self.wFIFO)
            self.wLRU = 1 - self.wFIFO
            del self.HFIFO[q]

    def _update_weight_lru_hit(self, lamb):
        self.wLRU = self.wLRU - lamb * (1 - self.wLRU)
        self.wFIFO = 1 - self.wLRU


    def access(self, cache_req: CacheRequest) -> None:
        self.accesses += 1
        q = cache_req.tag
        if q in self.Cache:
            self.hits += 1
            if random.random() < self.wLRU:
                self.Cache.move_to_end(q)
                self.Cache[q]=1
                self._update_weight_lru_hit(self.lamb * 0.01)
        else:
            self.misses += 1
            self._update_weight(q, self.lamb, 1)
            if len(self.Cache) == self.num_blocks:
                # if random.random() < self.wLRU:
                #     evicted = self._evict_from_order(self.LRU)
                #     if len(self.HLRU) >= self.num_blocks:
                #         self.HLRU.popitem(last=False)
                #     self.HLRU[evicted] = None
                # else:
                #     evicted = self._evict_from_order(self.FIFO)
                #     if len(self.HFIFO) >= self.num_blocks:
                #         self.HFIFO.popitem(last=False)
                #     self.HFIFO[evicted] = None
                self.evict()
                # self.evicts += 1
            self.Cache[q] = None

    def evict(self):
        # Eviction is handled in access method
        self.evicts += 1
        evicted = self.Cache.popitem(last=False)
        if(evicted[1]):
            if len(self.HLRU) >= self.num_blocks:
                self.HLRU.popitem(last=False)
            self.HLRU[evicted] = None
        else:
            if len(self.HFIFO) >= self.num_blocks:
                self.HFIFO.popitem(last=False)
            self.HFIFO[evicted] = None
