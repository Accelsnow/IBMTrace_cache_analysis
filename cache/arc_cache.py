from cache import BaseCache, CacheRequest
from collections import OrderedDict

class ARCCache(BaseCache):
    def __init__(self, size: int, block_size: int, filename: str):
        super().__init__(size, block_size, filename)
        self.name = "ARCache"
        self._p = 0
        self._t1 = OrderedDict()
        self._t2 = OrderedDict()
        self._b1 = OrderedDict()
        self._b2 = OrderedDict()

    def _replace(self, candidate: str):
        if candidate in self._t1 and len(self._t1) > self._p:
            key, _ = self._t1.popitem(last=False)
            self._b1[key] = None
            self.evicts += 1
        elif self._t2:
            key, _ = self._t2.popitem(last=False)
            self._b2[key] = None
            self.evicts += 1

    def access(self, cache_request: CacheRequest) -> None:
        self.accesses += 1
        key = cache_request.tag
        if key in self._t1 or key in self._t2:
            # Cache hit
            self.hits += 1
            if key in self._t1:
                del self._t1[key]
                self._t2[key] = None
            else:
                self._t2.move_to_end(key)
        else:
            # Cache miss
            self.misses += 1
            if key in self._b1:
                self._p = min(self._p + max(len(self._b2) // len(self._b1), 1), self.num_blocks)
                self._replace(key)
                del self._b1[key]
                self._t2[key] = None
            elif key in self._b2:
                self._p = max(self._p - max(len(self._b1) // len(self._b2), 1), 0)
                self._replace(key)
                del self._b2[key]
                self._t2[key] = None
            else:
                if len(self._t1) + len(self._b1) == self.num_blocks:
                    if len(self._t1) < self.num_blocks:
                        self._b1.popitem(last=False)
                        self._replace(key)
                    else:
                        self._t1.popitem(last=False)
                elif len(self._t1) + len(self._b1) < self.num_blocks and len(self._t1) + len(self._t2) + len(self._b1) + len(self._b2) >= self.num_blocks:
                    if len(self._t1) + len(self._t2) + len(self._b1) + len(self._b2) == 2 * self.num_blocks:
                        self._b2.popitem(last=False)
                    self._replace(key)
                self._t1[key] = None

    def evict(self) -> None:
        # This method is handled implicitly within the access method
        pass