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
        elif cache_size_str.endswith("T"):
            return int(cache_size_str[:-1]) * (1024 ** 4)
        elif cache_size_str.endswith("K"):
            return int(cache_size_str[:-1]) * (1024 ** 1)
        else:
            return int(cache_size_str)
    except ValueError:
        raise argparse.ArgumentTypeError(f"Invalid cache size: {cache_size_str}")


def parse_cache_type(cache_type: str, cache_size: int, block_size: int, evict_size: float, filename: str) -> BaseCache:
    if cache_type == 'fifo':
        return FIFOCache(cache_size, block_size, filename)
    elif cache_type == 'lru':
        return LRUCache(cache_size, block_size, filename)
    elif cache_type == 'our':
        return OurCache(cache_size, block_size, evict_size, filename)
    elif cache_type == 'arc':
        return ARCCache(cache_size, block_size, filename)
    elif cache_type == 'lec':
        return LeCaRCache(cache_size, block_size, filename)
    else:
        raise argparse.ArgumentTypeError(f"Invalid cache type: {cache_type}")


def get_file_paths(directory):
    paths = []

    for root, directories, files in os.walk(directory):
        for filename in files:
            if(not filename.endswith("Part0")):
                continue
            
            filepath = os.path.join(root, filename)
            new_filename = filename[:-1] + str(int(filename[-1]) + 1)
            filepaths = []
            filepaths.append(filepath)
            while(new_filename in files):
                new_filepath = os.path.join(root, filename)
                new_filename = new_filename[:-1] + str(int(new_filename[-1]) + 1)
                filepaths.append(new_filepath)
            if(len(filepaths) != 1):
                paths.append(filepaths)
            else:
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

    # assert cache_size % block_size == 0

    ibm_parser = IBMCOSTraceParser()

    c: BaseCache

    if mode == 0:
        c = parse_cache_type(cache_type, cache_size, block_size, evict_size, filename)
        cache_reqs = ibm_parser.parse_all(filename, block_size)
        for req in tqdm(cache_reqs):
            c.access(req)

        c.print_stats()
    elif mode == 1:
        assert cache_type == 'our'
        e_vals = [0.00001, 0.0001, 0.001, 0.01, 0.1, 100, 1000, 10000, 100000]

        cache_reqs = ibm_parser.parse_all(filename, block_size)

        for e in e_vals:
            c = parse_cache_type(cache_type, cache_size, block_size, e, filename)

            for req in tqdm(cache_reqs):
                c.access(req)

            c.print_stats()
    elif mode == 2:
        print(f"Running predefined set of experiments. Ignoring -f {filename} options.")
        file_paths = sorted(get_file_paths("data"), key=lambda x: x[0] if isinstance(x, list) else x)

        for file_path in file_paths:
            if isinstance(file_path, list):
                print("=============================")
                print(f"Running experiments on {file_path[0][:-5]}")
                c = parse_cache_type(cache_type, cache_size, block_size, evict_size, file_path[0])
                # avoid memory overflow, use parse and run
                for path in file_path:
                    ibm_parser.parse_and_run(path, c)
                c.print_stats()
                print("=============================\n")
            elif file_path.count("IBMObjectStoreTrace") == 1:
                print("=============================")
                print(f"Running experiments on {file_path}")
                c = parse_cache_type(cache_type, cache_size, block_size, evict_size, file_path)
                # avoid memory overflow, use parse and run
                ibm_parser.parse_and_run(file_path, c)
                c.print_stats()
                print("=============================\n")
    elif mode == 3:
        with open("./experiments/num_blocks.out", "r") as f:
            trace_sizes = f.readlines()
        trace_sizes = [int(x) for x in trace_sizes]
        i = 0
        print(f"Running predefined set of experiments. Ignoring -f {filename} options.")
        file_paths = sorted(get_file_paths("data"), key=lambda x: x[0] if isinstance(x, list) else x)
        # trace_size = 
        for file_path in file_paths:
            if i == 12 or i== 75:
                i+=1
                continue
            trace_size = trace_sizes[i]
            if trace_size < 100:
                i += 1
                continue
            if isinstance(file_path, list):
                print("=============================")
                print(f"Running experiments on {file_path[0][:-5]}" + " with "+str(cache_size)+"% cache size")
                # trace_size += ibm_parser.count_total_size(path, block_size, counted)
                percentage_cache_size = cache_size*trace_size//100*block_size + block_size 
                c = parse_cache_type(cache_type, percentage_cache_size, block_size, evict_size, file_path[0])
                # avoid memory overflow, use parse and run
                for path in file_path:
                    ibm_parser.parse_and_run(path, c)
                c.print_stats()
                print("=============================\n")
            elif file_path.count("IBMObjectStoreTrace") == 1:
                print("=============================")
                print(f"Running experiments on {file_path}" + " with "+str(cache_size) +"% cache size")
                # trace_size = ibm_parser.count_total_size(file_path, block_size, counted)
                percentage_cache_size = cache_size*trace_size//100*block_size + block_size
                c = parse_cache_type(cache_type, percentage_cache_size, block_size, evict_size, file_path)
                # avoid memory overflow, use parse and run
                ibm_parser.parse_and_run(file_path, c)
                c.print_stats()
                print("=============================\n")
            i+=1
    elif mode==4:
        file_paths = sorted(get_file_paths("data"), key=lambda x: x[0] if isinstance(x, list) else x)

        for file_path in file_paths:
            if isinstance(file_path, list):
                # print("=============================")
                # print(f"Running experiments on {file_path[0][:-5]}" + " with "+str(cache_size)+"% cache size")
                trace_size = 0
                counted = set()
                for path in file_path:
                    trace_size += ibm_parser.count_total_size(path, block_size, counted)
                # percentage_cache_size = cache_size*trace_size//100*block_size
                # c = parse_cache_type(cache_type, percentage_cache_size, block_size, evict_size, file_path[0])
                # avoid memory overflow, use parse and run
                print(trace_size)
                # for path in file_path:
                #     ibm_parser.parse_and_run(path, c)
                # c.print_stats()
                # print("=============================\n")
            elif file_path.count("IBMObjectStoreTrace") == 1:
                # print("=============================")
                # print(f"Running experiments on {file_path}" + " with "+str(cache_size) +"% cache size")
                counted = set()
                trace_size = ibm_parser.count_total_size(file_path, block_size, counted)
                print(trace_size)
                # percentage_cache_size = cache_size*trace_size//100*block_size
                # c = parse_cache_type(cache_type, percentage_cache_size, block_size, evict_size, file_path)
                # # avoid memory overflow, use parse and run
                # ibm_parser.parse_and_run(file_path, c)
                # c.print_stats()
                # print("=============================\n")
    else:
        raise argparse.ArgumentTypeError(f"Invalid mode: {mode}")


if __name__ == "__main__":
    main()
