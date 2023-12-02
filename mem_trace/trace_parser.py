from __future__ import annotations

from typing import List

from mem_trace import Trace


class TraceParser:
    def parse(self, trace_filename: str) -> List[Trace]:
        raise NotImplementedError


class IBMCOSTraceParser(TraceParser):
    def parse(self, trace_filename: str) -> List[Trace]:
        raise NotImplementedError
