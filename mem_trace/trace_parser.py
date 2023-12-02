from __future__ import annotations

from typing import List

from cache import CacheRequest


class TraceParser:
    def parse(self, trace_filename: str) -> List[CacheRequest]:
        raise NotImplementedError


class IBMCOSTraceParser(TraceParser):
    def parse(self, trace_filename: str) -> List[CacheRequest]:
        raise NotImplementedError
