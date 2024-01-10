from __future__ import annotations

from typing import List

from cache import *

from tqdm import tqdm


PARSE_REQ_LIMIT = 500000000


class TraceParser:
    def parse_all(self, trace_filename: str, block_size: int) -> List[CacheRequest]:
        raise NotImplementedError

    def parse_and_run(self, trace_filename: str, cache: BaseCache) -> None:
        raise NotImplementedError


class IBMCOSTraceParser(TraceParser):
    @staticmethod
    def _get_line_cache_reqs(line: str, block_size: int) -> List[CacheRequest]:
        line = line.split(' ')
        tags = []
        acc_type: AccessType
        if len(line) != 6:
            if line[2] == "REST.PUT.OBJECT":
                acc_type = AccessType.WRITE
                tot_size = int(line[3])
                blk_num = (tot_size - 1) // block_size + 1

                for i in range(blk_num):
                    tag = (int(line[2], 16), i)
                    tags.append(tag)
            elif line[2] == "REST.COPY.OBJECT":
                tot_size = int(line[3])
                blk_num = (tot_size - 1) // block_size + 1
                for i in range(blk_num):
                    tag = (int(line[2], 16), i)
                    tags.append(tag)
                acc_type = AccessType.READ
            elif line[2] == "REST.DELETE.OBJECT":
                tot_size = int(line[3])
                blk_num = (tot_size - 1) // block_size + 1
                for i in range(blk_num):
                    tag = (int(line[2], 16), i)
                    tags.append(tag)
                acc_type = AccessType.DELETE
            else:
                tags.append((-int(line[2], 16), 1))
                acc_type = AccessType.READ
        else:
            acc_type = AccessType.READ
            begin_block = int(line[4]) // block_size
            end_block = int(line[5]) // block_size
            for i in range(begin_block, end_block + 1):
                tag = (int(line[2], 16), i)
                tags.append(tag)
        cache_requests = []
        for tag in tags:
            cache_requests.append(CacheRequest(tag, acc_type))
        return cache_requests

    def count_total_size(self, trace_filename: str, block_size: int, alreadys: set) -> int:
        with open(trace_filename, "r") as trace:
            total_size = 0
            for line in tqdm(trace.readlines()):
                line = line.split(' ')
                if len(line) != 6:
                    if line[2] == "REST.PUT.OBJECT":
                        tot_size = int(line[3])
                        blk_num = (tot_size - 1) // block_size + 1
                        if line[2] not in alreadys:
                            total_size += blk_num
                            alreadys.add(line[2])
                    elif line[2] == "REST.COPY.OBJECT":
                        tot_size = int(line[3])
                        blk_num = (tot_size - 1) // block_size + 1
                        if line[2] not in alreadys:
                            total_size += blk_num
                            alreadys.add(line[2])
                    elif line[2] == "REST.DELETE.OBJECT":
                        tot_size = int(line[3])
                        blk_num = (tot_size - 1) // block_size + 1
                        if line[2] not in alreadys:
                            total_size += blk_num
                            alreadys.add(line[2])
                    else:
                        if line[2] not in alreadys:
                            total_size += 1
                            alreadys.add(line[2])
                else:
                    begin_block = int(line[4]) // block_size
                    end_block = int(line[5]) // block_size
                    for i in range(begin_block, end_block + 1):
                        tag = (int(line[2], 16), i)
                        if tag not in alreadys:
                            total_size += 1
                            alreadys.add(tag)
            return total_size
    
    def parse_and_run(self, trace_filename: str, cache: BaseCache) -> None:
        with open(trace_filename, "r") as trace:
            for line in tqdm(trace.readlines()):
                reqs = self._get_line_cache_reqs(line, cache.block_size)
                for req in reqs:
                    cache.access(req)

    def parse_all(self, trace_filename: str, block_size: int) -> List[CacheRequest]:
        with open(trace_filename, "r") as trace:
            cache_requests = []
            for line in tqdm(trace.readlines()):
                cache_requests.extend(self._get_line_cache_reqs(line, block_size))
                if len(cache_requests) > PARSE_REQ_LIMIT:
                    print(f"NUM REQUESTS > {PARSE_REQ_LIMIT}!!! {trace_filename} PARSING STOPPED!")
                    break
            return cache_requests


class MSRTraceParser(TraceParser):
    def parse_all(self, trace_filename: str, block_size: int) -> List[CacheRequest]:
        with open(trace_filename, "r") as trace:
            cache_requests = []
            for line in tqdm(trace.readlines()):
                acc_type: AccessType
                line = line.split(',')
                tags = []
                blk_num = (int(5)) // block_size
                if line[3] == "Write":
                    acc_type = AccessType.WRITE
                else:
                    acc_type = AccessType.READ
                for i in range(blk_num):
                    tag = (int(line[0]), i)
                    tags.append(tag)

                for tag in tags:
                    cache_requests.append(CacheRequest(tag, acc_type))

                if len(cache_requests) > PARSE_REQ_LIMIT:
                    print(f"NUM REQUESTS > {PARSE_REQ_LIMIT}!!! {trace_filename} PARSING STOPPED!")
                    break
            return cache_requests
