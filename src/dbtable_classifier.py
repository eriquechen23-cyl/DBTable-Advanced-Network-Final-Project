from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
import sys
from typing import Iterable

from classbench import Packet, Rule, rule_matches


@dataclass(frozen=True, slots=True)
class BuildStats:
    selected_bits: tuple[int, ...]
    bucket_count: int
    average_bucket_size: float
    max_bucket_size: int
    fallback_rules: int
    replicated_entries: int
    estimated_memory_bytes: int


class DBTableClassifier:
    """DBTable-inspired packet classifier for ClassBench five-tuple rules.

    The implementation follows the DBTable idea of using discriminative IP bits
    to reduce the candidate rule set before exact five-tuple verification. It is
    intentionally compact for reproducible coursework experiments.
    """

    def __init__(
        self,
        rules: Iterable[Rule],
        bit_count: int = 12,
        max_replication_bits: int = 12,
    ) -> None:
        self.rules = sorted(list(rules), key=lambda r: r.priority)
        self.bit_count = bit_count
        self.max_replication_bits = max_replication_bits
        self.selected_bits: tuple[int, ...] = ()
        self.buckets: dict[int, list[int]] = {}
        self.fallback: list[int] = []
        self.stats: BuildStats | None = None

    def build(self) -> BuildStats:
        self.selected_bits = tuple(self._choose_bits(self.bit_count))
        bucket_map: dict[int, list[int]] = defaultdict(list)
        fallback: list[int] = []
        replicated_entries = 0

        for idx, rule in enumerate(self.rules):
            keys = self._rule_signatures(rule)
            if keys is None:
                fallback.append(idx)
                continue
            for key in keys:
                bucket_map[key].append(idx)
                replicated_entries += 1

        self.buckets = {
            key: sorted(indices, key=lambda i: self.rules[i].priority)
            for key, indices in bucket_map.items()
        }
        self.fallback = sorted(fallback, key=lambda i: self.rules[i].priority)

        sizes = [len(v) for v in self.buckets.values()]
        stats = BuildStats(
            selected_bits=self.selected_bits,
            bucket_count=len(self.buckets),
            average_bucket_size=(sum(sizes) / len(sizes)) if sizes else 0.0,
            max_bucket_size=max(sizes) if sizes else 0,
            fallback_rules=len(self.fallback),
            replicated_entries=replicated_entries,
            estimated_memory_bytes=self._estimate_memory(),
        )
        self.stats = stats
        return stats

    def search(self, packet: Packet) -> int:
        best_priority: int | None = None
        key = self._packet_signature(packet)

        for idx in self.buckets.get(key, []):
            rule = self.rules[idx]
            if best_priority is not None and rule.priority >= best_priority:
                break
            if rule_matches(rule, packet):
                best_priority = rule.priority
                break

        for idx in self.fallback:
            rule = self.rules[idx]
            if best_priority is not None and rule.priority >= best_priority:
                break
            if rule_matches(rule, packet):
                best_priority = rule.priority
                break

        return -1 if best_priority is None else best_priority

    def _choose_bits(self, bit_count: int) -> list[int]:
        scored: list[tuple[float, int]] = []
        total = len(self.rules) or 1
        for bit in range(64):
            zero = one = wildcard = 0
            for rule in self.rules:
                value = self._rule_bit(rule, bit)
                if value is None:
                    wildcard += 1
                elif value == 0:
                    zero += 1
                else:
                    one += 1
            balance = min(zero, one)
            coverage = (total - wildcard) / total
            score = balance * coverage
            scored.append((score, bit))
        scored.sort(key=lambda item: (-item[0], item[1]))
        return [bit for score, bit in scored[:bit_count] if score > 0]

    def _rule_signatures(self, rule: Rule) -> list[int] | None:
        keys = [0]
        wildcard_count = 0
        for bit in self.selected_bits:
            value = self._rule_bit(rule, bit)
            if value is None:
                wildcard_count += 1
                if wildcard_count > self.max_replication_bits:
                    return None
                keys = [(key << 1) for key in keys] + [((key << 1) | 1) for key in keys]
            else:
                keys = [(key << 1) | value for key in keys]
        return keys

    def _packet_signature(self, packet: Packet) -> int:
        key = 0
        for bit in self.selected_bits:
            if bit < 32:
                value = (packet.src_ip >> (31 - bit)) & 1
            else:
                value = (packet.dst_ip >> (63 - bit)) & 1
            key = (key << 1) | value
        return key

    @staticmethod
    def _rule_bit(rule: Rule, bit: int) -> int | None:
        if bit < 32:
            if rule.src_len <= bit:
                return None
            return (rule.src_ip >> (31 - bit)) & 1
        dst_bit = bit - 32
        if rule.dst_len <= dst_bit:
            return None
        return (rule.dst_ip >> (31 - dst_bit)) & 1

    def _estimate_memory(self) -> int:
        total = sys.getsizeof(self.rules) + sys.getsizeof(self.buckets) + sys.getsizeof(self.fallback)
        total += len(self.rules) * sys.getsizeof(self.rules[0]) if self.rules else 0
        for key, values in self.buckets.items():
            total += sys.getsizeof(key) + sys.getsizeof(values)
            total += len(values) * 4
        total += len(self.fallback) * 4
        return total
