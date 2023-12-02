from mem_trace import Trace


class BaseCache:
    name: str
    hits: int
    evicts: int
    misses: int
    accesses: int
    size: int
    block_size: int
    num_blocks: int

    def __init__(self, size: int, block_size: int):
        self.name = "BaseCache"
        self.hits = 0
        self.evicts = 0
        self.misses = 0
        self.accesses = 0
        self.size = size
        self.block_size = block_size
        assert size % block_size == 0
        self.num_blocks = size // block_size

    def hit_rate(self) -> float:
        assert self.hits + self.misses == self.accesses
        return self.hits / self.accesses

    def miss_rate(self) -> float:
        assert self.hits + self.misses == self.accesses
        return self.misses / self.accesses

    def __str__(self):
        return f"{self.name} - hits: {self.hits}, misses: {self.misses}, evicts: {self.evicts}, accesses: {self.accesses}, hit_rate: {self.hit_rate()}, miss_rate: {self.miss_rate()}"

    def print_stats(self) -> None:
        print(str(self))

    def access(self, trace: Trace) -> None:
        raise NotImplementedError

    def evict(self) -> None:
        raise NotImplementedError
