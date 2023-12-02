from cache import *
from mem_trace import *
from tqdm import tqdm
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('-c', type=str, required=True)
parser.add_argument('-b', type=int, required=True)


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


if __name__ == "__main__":
    args = parser.parse_args()

    cache_size = parse_cache_size(args.c)
    block_size = args.b

    assert cache_size % block_size == 0

    c = FIFOCache(cache_size, block_size)

    ibm_parser = IBMCOSTraceParser()
    cache_reqs = ibm_parser.parse("IBMObjectStoreSample")

    for req in tqdm(cache_reqs):
        c.access(req)

    c.print_stats()
