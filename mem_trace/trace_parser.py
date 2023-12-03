from __future__ import annotations

from typing import List

from cache import *

from tqdm import tqdm


PARSE_REQ_LIMIT = 500000000


class TraceParser:
    def parse_all(self, trace_filename: str) -> List[CacheRequest]:
        raise NotImplementedError

    def parse_and_run(self, trace_filename: str, cache: BaseCache) -> None:
        raise NotImplementedError


class IBMCOSTraceParser(TraceParser):
    @staticmethod
    def _get_line_cache_reqs(line: str) -> List[CacheRequest]:
        line = line.split(',')
        tags = []
        acc_type: AccessType
        if len(line) != 6:
            if line[2] == "REST.PUT.OBJECT":
                acc_type = AccessType.WRITE
                tot_size = int(line[3])
                blk_num = (tot_size - 1) // 4096 + 1

                for i in range(blk_num):
                    tag = (int(line[2], 16), i)
                    tags.append(tag)
            elif line[2] == "REST.COPY.OBJECT":
                tot_size = int(line[3])
                blk_num = (tot_size - 1) // 4096 + 1
                for i in range(blk_num):
                    tag = (int(line[2], 16), i)
                    tags.append(tag)
                acc_type = AccessType.READ
            elif line[2] == "REST.DELETE.OBJECT":
                tot_size = int(line[3])
                blk_num = (tot_size - 1) // 4096 + 1
                for i in range(blk_num):
                    tag = (int(line[2], 16), i)
                    tags.append(tag)
                acc_type = AccessType.DELETE
            else:
                tags.append((-int(line[2], 16), 1))
                acc_type = AccessType.READ
        else:
            acc_type = AccessType.READ
            begin_block = int(line[4]) // 4096
            end_block = int(line[5]) // 4096
            for i in range(begin_block, end_block + 1):
                tag = (int(line[2], 16), i)
                tags.append(tag)
        cache_requests = []
        for tag in tags:
            cache_requests.append(CacheRequest(tag, acc_type))
        return cache_requests

    def parse_and_run(self, trace_filename: str, cache: BaseCache) -> None:
        with open(trace_filename, "r") as trace:
            while True:
                line = trace.readline()
                if not line:
                    break
                reqs = self._get_line_cache_reqs(line)
                for req in reqs:
                    cache.access(req)

    def parse_all(self, trace_filename: str) -> List[CacheRequest]:
        with open(trace_filename, "r") as trace:
            cache_requests = []
            for line in tqdm(trace.readlines()):
                cache_requests.extend(self._get_line_cache_reqs(line))
                if len(cache_requests) > PARSE_REQ_LIMIT:
                    print(f"NUM REQUESTS > {PARSE_REQ_LIMIT}!!! {trace_filename} PARSING STOPPED!")
                    break
            return cache_requests


class MSRTraceParser(TraceParser):
    def parse_all(self, trace_filename: str) -> List[CacheRequest]:
        with open(trace_filename, "r") as trace:
            cache_requests = []
            for line in tqdm(trace.readlines()):
                acc_type: AccessType
                line = line.split(',')
                tags = []
                blk_num = (int(5)) // 4096
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
