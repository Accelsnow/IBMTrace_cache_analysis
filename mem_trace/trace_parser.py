from __future__ import annotations

from typing import List

from cache import CacheRequest

from mem_trace import AccessType

import tarfile

import os

class TraceParser:
    def parse(self, trace_filename: str) -> List[CacheRequest]:
        raise NotImplementedError


class IBMCOSTraceParser(TraceParser):
    def parse(self, trace_filename: str) -> List[CacheRequest]:
        
        with open(trace_filename, "r") as trace: 
            cache_requests = []
            for line in trace:
                line = line.split()
                tags = []
                if len(line)!=6:
                    if line[2] == "REST.PUT.OBJECT":
                        acc_type = AccessType.WRITE
                        tot_size = int(line[3])
                        blk_num = tot_size//4096 + 1
                        
                        for i in range(blk_num):
                            tag = (int(line[2]), i)
                            tags.append(tag)
                    elif line[2] == "REST.COPY.OBJECT":
                        tot_size = int(line[3])
                        blk_num = tot_size//4096 + 1
                        for i in range(blk_num):
                            tag = (int(line[2]), i)
                            tags.append(tag)
                        acc_type = AccessType.READ
                    elif line[2] == "REST.DELETE.OBJECT":
                        tot_size = int(line[3])
                        blk_num = tot_size//4096 + 1
                        for i in range(blk_num):
                            tag = (int(line[2]), i)
                            tags.append(tag)
                        acc_type = AccessType.DELETE
                    else:
                        tag = (-int(line[2]), 1)
                        acc_type = AccessType.READ
                else:
                    acc_type = AccessType.READ
                    begin_block = int(line[4])//4096
                    end_block = int(line[5])//4096
                    for i in range(begin_block, end_block+1):
                        tag = (int(line[2]), i)
                        tags.append(tag)          
                
                for tag in tags:
                    cache_request = CacheRequest(tag, acc_type)
                    cache_requests.append(cache_request)
            return cache_requests
