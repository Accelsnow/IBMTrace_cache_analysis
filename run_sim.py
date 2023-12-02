from cache import *
from mem_trace import *
from tqdm import tqdm
import argparse
import os

parser = argparse.ArgumentParser()
parser.add_argument('-c', type=str, required=True)
parser.add_argument('-b', type=int, required=True)
parser.add_argument('-f', type=str, required=True)
parser.add_argument('-t', type=str, required=True)
parser.add_argument('-e', type=float, default=0.01)
parser.add_argument('-m', type=int, required=True)


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


def parse_cache_type(cache_type: str, cache_size: int, block_size: int, evict_size: float) -> BaseCache:
    if cache_type == 'fifo':
        return FIFOCache(cache_size, block_size)
    elif cache_type == 'lru':
        return LRUCache(cache_size, block_size)
    elif cache_type == 'our':
        return OurCache(cache_size, block_size, evict_size)
    else:
        raise argparse.ArgumentTypeError(f"Invalid cache type: {cache_type}")


def get_file_paths(directory):
    paths = []

    for root, directories, files in os.walk(directory):
        for filename in files:
            filepath = os.path.join(root, filename)
            paths.append(filepath)

    return paths


def main():
    args = parser.parse_args()

    cache_size = parse_cache_size(args.c)
    block_size = args.b
    filename = args.f
    cache_type = args.t
    evict_size = args.e
    mode = args.m

    assert cache_size % block_size == 0

    ibm_parser = IBMCOSTraceParser()

    c: BaseCache

    if mode == 0:
        c = parse_cache_type(cache_type, cache_size, block_size, evict_size)
        cache_reqs = ibm_parser.parse(filename)
        for req in tqdm(cache_reqs):
            c.access(req)

        c.print_stats()
    elif mode == 1:
        assert cache_type == 'our'
        e_vals = [0.00001, 0.0001, 0.001, 0.01, 0.1, 100, 1000, 10000, 100000]

        cache_reqs = ibm_parser.parse(filename)

        for e in e_vals:
            c = parse_cache_type(cache_type, cache_size, block_size, e)

            for req in tqdm(cache_reqs):
                c.access(req)

            c.print_stats()
    elif mode == 2:
        print(f"Running predefined set of experiments. Ignoring -t {cache_type} and -f {filename} options.")
        file_paths = get_file_paths("data")

        for file in file_paths:
            if file.startswith("IBM"):
                print("=============================")
                print(f"Running experiments on {file}")
                cache_reqs = ibm_parser.parse(file)
                for cache_type in ['fifo', 'lru', 'our']:
                    c = parse_cache_type(cache_type, cache_size, block_size, evict_size)
                    for req in tqdm(cache_reqs):
                        c.access(req)

                    c.print_stats()
                print("=============================\n")

    else:
        raise argparse.ArgumentTypeError(f"Invalid mode: {mode}")


if __name__ == "__main__":
    main()
