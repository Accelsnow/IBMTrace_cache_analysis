from __future__ import annotations

from typing import List

from cache import CacheRequest

import tarfile

import os

class TraceParser:
    def parse(self, trace_filename: str) -> List[CacheRequest]:
        raise NotImplementedError


class IBMCOSTraceParser(TraceParser):
    def parse(self, trace_filename: str) -> List[CacheRequest]:
        
        if os.path.isdir(trace_filename+'_files'):
            tracesObjs = os.listdir(trace_filename+'_files')
            for trace in tracesObjs:
                trace = open(trace)
                for line in trace:
                    line = line.split()
                    
                    if len(line)!=6:
                        if line[2] == "REST.PUT.OBJECT":
                            tag = (int(line[2]), -1)
                            tot_size = int(line[3])
                            acc_start = 0
                            acc_end = tot_size-1
                            acc_type = AccessType.WRITE
                        elif line[2] == "REST.COPY.OBJECT":
                            tag = (int(line[2]), -1)
                            tot_size = int(line[3])
                            acc_start = 0
                            acc_end = tot_size-1
                            acc_type = AccessType.READ
                        elif line[2] == "REST.DELETE.OBJECT":
                            tag = (int(line[2]), -1)
                            tot_size = int(line[3])
                            acc_start = 0
                            acc_end = tot_size-1
                            acc_type = AccessType.DELETE
                        else:
                            tag = -int(line[2])
                            tot_size = 4096
                            acc_start = 0
                            acc_end = 4095
                            acc_type = AccessType.READ
                    else:
                        tag = int(line[2])
                        tot_size = int(line[3])
                        acc_start = int(line[4])
                        acc_end = int(line[5])
                        acc_type = AccessType.READ
                    trace = Trace(tag, tot_size, acc_start, acc_end, acc_type)
                    tracesObjs.append(trace)
        else:
            tracesObjs = tarfile.open(trace_filename)
            os.mkdir(trace_filename+'_files')
            if 
        
        raise NotImplementedError
