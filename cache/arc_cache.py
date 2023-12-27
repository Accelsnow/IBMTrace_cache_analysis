from cache import BaseCache, CacheRequest
from collections import OrderedDict

class ARCCache(BaseCache):
    def __init__(self, size: int, block_size: int, filename: str):
        super().__init__(size, block_size, filename)
        self.name = "ARCCache"
        self.p = 0  # Adaptive parameter balancing LRU and LFU
        self.t1 = OrderedDict()  # LRU list
        self.t2 = OrderedDict()  # LFU list
        self.b1 = OrderedDict()  # LRU ghost list
        self.b2 = OrderedDict()  # LFU ghost list

    def replace(self, tag):
        if len(self.t1) > 0 and (tag in self.b2 or len(self.t1) > self.p):
            old_tag, _ = self.t1.popitem(last=False)
            self.b1[old_tag] = 1
        else:
            old_tag, _ = self.t2.popitem(last=False)
            self.b2[old_tag] = 1

    def access(self, cache_request: CacheRequest) -> None:
        self.accesses += 1
        tag = cache_request.tag

        # Case 1: Hit in t1 or t2
        if tag in self.t1:
            self.hits += 1
            self.t1.pop(tag)
            self.t2[tag] = 1
        elif tag in self.t2:
            self.hits += 1
            self.t2.move_to_end(tag)
        
        # Case 2: Miss but in b1 or b2
        elif tag in self.b1:
            self.misses += 1
            self.p = min(self.p + max(len(self.b2) / len(self.b1), 1), self.num_blocks)
            self.replace(tag)
            self.b1.pop(tag)
            self.t2[tag] = 1
        elif tag in self.b2:
            self.misses += 1
            self.p = max(self.p - max(len(self.b1) / len(self.b2), 1), 0)
            self.replace(tag)
            self.b2.pop(tag)
            self.t2[tag] = 1

        # Case 3: Complete miss
        else:
            self.misses += 1
            if len(self.t1) + len(self.b1) == self.num_blocks:
                if len(self.t1) < self.num_blocks:
                    self.b1.popitem(last=False)
                    self.replace(tag)
                else:
                    self.evict()
            elif len(self.t1) + len(self.b1) < self.num_blocks and len(self.t1) + len(self.t2) + len(self.b1) + len(self.b2) >= self.num_blocks:
                if len(self.t1) + len(self.t2) + len(self.b1) + len(self.b2) == 2 * self.num_blocks:
                    self.b2.popitem(last=False)
                self.replace(tag)
            self.t1[tag] = 1

    def evict(self) -> None:
        self.evicts += 1
        self.t1.popitem(last=False)
