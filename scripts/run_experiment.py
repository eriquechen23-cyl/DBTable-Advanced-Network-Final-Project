from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
import statistics
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
sys.path.insert(0, str(SRC))

from classbench import count_lines, iter_packets, load_rules
from dbtable_classifier import DBTableClassifier


def percentile(values: list[float], pct: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    k = int(round((pct / 100.0) * (len(ordered) - 1)))
    return ordered[k]


def run(args: argparse.Namespace) -> dict:
    rules_path = Path(args.rules)
    trace_path = Path(args.trace)

    load_start = time.perf_counter()
    rules = load_rules(rules_path, limit=args.rule_limit)
    load_seconds = time.perf_counter() - load_start

    build_start = time.perf_counter()
    classifier = DBTableClassifier(
        rules,
        bit_count=args.bits,
        max_replication_bits=args.max_replication_bits,
    )
    build_stats = classifier.build()
    build_seconds = time.perf_counter() - build_start

    latencies_ns: list[float] = []
    match_count = 0
    packet_count = 0
    lookup_start = time.perf_counter()
    for packet in iter_packets(trace_path, limit=args.max_traces):
        packet_count += 1
        start = time.perf_counter_ns()
        result = classifier.search(packet)
        end = time.perf_counter_ns()
        latencies_ns.append(end - start)
        if result >= 0:
            match_count += 1
    lookup_seconds = time.perf_counter() - lookup_start

    summary = {
        "rules_file": str(rules_path),
        "trace_file": str(trace_path),
        "rules_loaded": len(rules),
        "rules_file_lines": count_lines(rules_path),
        "packets_tested": packet_count,
        "matched_packets": match_count,
        "selected_bits": list(build_stats.selected_bits),
        "bucket_count": build_stats.bucket_count,
        "average_bucket_size": build_stats.average_bucket_size,
        "max_bucket_size": build_stats.max_bucket_size,
        "fallback_rules": build_stats.fallback_rules,
        "replicated_entries": build_stats.replicated_entries,
        "estimated_memory_bytes": build_stats.estimated_memory_bytes,
        "load_seconds": load_seconds,
        "build_seconds": build_seconds,
        "lookup_total_seconds": lookup_seconds,
        "lookup_avg_ns": statistics.fmean(latencies_ns) if latencies_ns else 0,
        "lookup_median_ns": statistics.median(latencies_ns) if latencies_ns else 0,
        "lookup_p95_ns": percentile(latencies_ns, 95),
        "lookup_p99_ns": percentile(latencies_ns, 99),
        "throughput_mpps": (packet_count / lookup_seconds / 1_000_000) if lookup_seconds else 0,
    }
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description="Run a DBTable-inspired ClassBench benchmark.")
    parser.add_argument("--rules", default=str(ROOT / "data" / "classbench" / "acl1_100000.txt"))
    parser.add_argument("--trace", default=str(ROOT / "data" / "classbench" / "acl1_100000.txt_trace"))
    parser.add_argument("--rule-limit", type=int, default=None)
    parser.add_argument("--max-traces", type=int, default=20000)
    parser.add_argument("--bits", type=int, default=12)
    parser.add_argument("--max-replication-bits", type=int, default=12)
    parser.add_argument("--out-json", default=str(ROOT / "results" / "dbtable_results.json"))
    parser.add_argument("--out-csv", default=str(ROOT / "results" / "dbtable_results.csv"))
    args = parser.parse_args()

    summary = run(args)
    out_json = Path(args.out_json)
    out_csv = Path(args.out_csv)
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    with out_csv.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(summary.keys()))
        writer.writeheader()
        writer.writerow(summary)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
