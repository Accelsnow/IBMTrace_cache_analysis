from cache import CacheRequest


class BaseCache:
    name: str
    description: str
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
        self.description = f"{size}/{block_size}, {self.num_blocks} blks, "

    def hit_rate(self) -> float:
        assert self.hits + self.misses == self.accesses
        return self.hits / self.accesses

    def miss_rate(self) -> float:
        assert self.hits + self.misses == self.accesses
        return self.misses / self.accesses

    def __str__(self):
        return f"{self.name} {self.description}\naccesses: {self.accesses}\nhits: {self.hits}\nmisses: {self.misses}\nevicts: {self.evicts}\nhit_rate: {self.hit_rate()}\nmiss_rate: {self.miss_rate()}\n\n"

    def print_stats(self) -> None:
        print(str(self))

    def access(self, cache_request: CacheRequest) -> None:
        raise NotImplementedError

    def evict(self) -> None:
        raise NotImplementedError
