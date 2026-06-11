from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import ipaddress
import re
from typing import Iterable, Iterator


RULE_RE = re.compile(
    r"^@(?P<sip>[0-9.]+)/(?P<slen>\d+)\s+"
    r"(?P<dip>[0-9.]+)/(?P<dlen>\d+)\s+"
    r"(?P<sp0>\d+)\s*:\s*(?P<sp1>\d+)\s+"
    r"(?P<dp0>\d+)\s*:\s*(?P<dp1>\d+)\s+"
    r"(?P<proto>0x[0-9a-fA-F]+)/(?P<pmask>0x[0-9a-fA-F]+)"
)


@dataclass(frozen=True, slots=True)
class Rule:
    priority: int
    src_ip: int
    src_len: int
    dst_ip: int
    dst_len: int
    src_port_lo: int
    src_port_hi: int
    dst_port_lo: int
    dst_port_hi: int
    proto_value: int
    proto_mask: int


@dataclass(frozen=True, slots=True)
class Packet:
    src_ip: int
    dst_ip: int
    src_port: int
    dst_port: int
    proto: int


def ipv4_to_int(value: str) -> int:
    return int(ipaddress.IPv4Address(value))


def parse_rule_line(line: str, priority: int) -> Rule | None:
    text = line.strip()
    if not text or text.startswith("#"):
        return None
    match = RULE_RE.match(text)
    if not match:
        return None
    g = match.groupdict()
    return Rule(
        priority=priority,
        src_ip=ipv4_to_int(g["sip"]),
        src_len=int(g["slen"]),
        dst_ip=ipv4_to_int(g["dip"]),
        dst_len=int(g["dlen"]),
        src_port_lo=int(g["sp0"]),
        src_port_hi=int(g["sp1"]),
        dst_port_lo=int(g["dp0"]),
        dst_port_hi=int(g["dp1"]),
        proto_value=int(g["proto"], 16),
        proto_mask=int(g["pmask"], 16),
    )


def load_rules(path: str | Path, limit: int | None = None) -> list[Rule]:
    rules: list[Rule] = []
    with Path(path).open("r", encoding="utf-8", errors="ignore") as fh:
        for line_no, line in enumerate(fh):
            parsed = parse_rule_line(line, line_no)
            if parsed is not None:
                rules.append(parsed)
                if limit is not None and len(rules) >= limit:
                    break
    return rules


def parse_trace_line(line: str) -> Packet | None:
    text = line.strip()
    if not text or text.startswith("#"):
        return None
    parts = text.split()
    if len(parts) < 5:
        return None
    return Packet(
        src_ip=int(parts[0]),
        dst_ip=int(parts[1]),
        src_port=int(parts[2]),
        dst_port=int(parts[3]),
        proto=int(parts[4]),
    )


def iter_packets(path: str | Path, limit: int | None = None) -> Iterator[Packet]:
    yielded = 0
    with Path(path).open("r", encoding="utf-8", errors="ignore") as fh:
        for line in fh:
            packet = parse_trace_line(line)
            if packet is None:
                continue
            yield packet
            yielded += 1
            if limit is not None and yielded >= limit:
                break


def rule_matches(rule: Rule, packet: Packet) -> bool:
    if not _prefix_match(packet.src_ip, rule.src_ip, rule.src_len):
        return False
    if not _prefix_match(packet.dst_ip, rule.dst_ip, rule.dst_len):
        return False
    if not (rule.src_port_lo <= packet.src_port <= rule.src_port_hi):
        return False
    if not (rule.dst_port_lo <= packet.dst_port <= rule.dst_port_hi):
        return False
    return (packet.proto & rule.proto_mask) == (rule.proto_value & rule.proto_mask)


def _prefix_match(packet_ip: int, rule_ip: int, length: int) -> bool:
    if length == 0:
        return True
    mask = (0xFFFFFFFF << (32 - length)) & 0xFFFFFFFF
    return (packet_ip & mask) == (rule_ip & mask)


def count_lines(path: str | Path) -> int:
    with Path(path).open("rb") as fh:
        return sum(1 for _ in fh)


def sample_rules(rules: Iterable[Rule], size: int) -> list[Rule]:
    result: list[Rule] = []
    for rule in rules:
        result.append(rule)
        if len(result) >= size:
            break
    return result
