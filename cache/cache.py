"""
SSD Cache
"""
class Cache:

    hits: int
    evicts: int
    misses: int
    accesses: int

    def __init__(self):
        self.hits = 0
        self.evicts = 0
        self.misses = 0
        self.accesses = 0


    def hit_rate(self) -> float:
        return self.hits / self.accesses

    def miss_rate(self) -> float:
        return self.misses / self.accesses

    def __str__(self):
        return f"{self.name} - hits: {self.hits}, misses: {self.misses}, evicts: {self.evicts}, accesses: {self.accesses}, hit_rate: {self.hit_rate()}, miss_rate: {self.miss_rate()}"

    def access(self) -> None:
        raise NotImplementedError

    def evict(self) -> None:
        raise NotImplementedError
