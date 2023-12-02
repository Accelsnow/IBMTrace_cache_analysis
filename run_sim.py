from cache import *
from mem_trace import *
from tqdm import tqdm
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('-c', type=str, required=True)
parser.add_argument('-b', type=int, required=True)
parser.add_argument('-f', type=str, required=True)
parser.add_argument('-t', type=str, required=True)


def parse_cache_size(cache_size_str: str) -> int:
    try:
        if cache_size_str.endswith("M"):
            return int(cache_size_str[:-1]) * (1024 ** 2)
        elif cache_size_str.endswith("G"):
            return int(cache_size_str[:-1]) * (1024 ** 3)
        elif cache_size_str.endswith("K"):
            return int(cache_size_str[:-1]) * (1024 ** 1)
        else:
            return int(cache_size_str)
    except ValueError:
        raise argparse.ArgumentTypeError(f"Invalid cache size: {cache_size_str}")


def parse_cache_type(cache_type: str, cache_size: int, block_size: int) -> BaseCache:
    if cache_type == 'fifo':
        return FIFOCache(cache_size, block_size)
    elif cache_type == 'lru':
        return LRUCache(cache_size, block_size)
    elif cache_type == 'our':
        return OurCache(cache_size, block_size)
    else:
        raise argparse.ArgumentTypeError(f"Invalid cache type: {cache_type}")


if __name__ == "__main__":
    args = parser.parse_args()

    cache_size = parse_cache_size(args.c)
    block_size = args.b
    filename = args.f

    assert cache_size % block_size == 0

    c = parse_cache_type(args.t, cache_size, block_size)

    ibm_parser = IBMCOSTraceParser()
    cache_reqs = ibm_parser.parse(filename)

    for req in tqdm(cache_reqs):
        c.access(req)

    c.print_stats()
