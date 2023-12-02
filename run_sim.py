from cache import FIFOCache
from mem_trace import IBMCOSTraceParser
from tqdm import tqdm

if __name__ == "__main__":
    c = FIFOCache(10 * (1024 ** 3), 4096)

    ibm_parser = IBMCOSTraceParser()
    cache_reqs = ibm_parser.parse("IBMObjectStoreSample")

    for req in tqdm(cache_reqs):
        c.access(req)

    c.print_stats()
