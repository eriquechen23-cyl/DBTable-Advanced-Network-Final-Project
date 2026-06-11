from __future__ import annotations

import argparse
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
sys.path.insert(0, str(SRC))

from classbench import iter_packets, load_rules, rule_matches
from dbtable_classifier import DBTableClassifier


def linear_search(rules, packet) -> int:
    for rule in rules:
        if rule_matches(rule, packet):
            return rule.priority
    return -1


def main() -> None:
    parser = argparse.ArgumentParser(description="Compare DBTable-inspired lookup against linear scan.")
    parser.add_argument("--rules", default=str(ROOT / "data" / "classbench" / "acl1_100000.txt"))
    parser.add_argument("--trace", default=str(ROOT / "data" / "classbench" / "acl1_100000.txt_trace"))
    parser.add_argument("--samples", type=int, default=200)
    parser.add_argument("--bits", type=int, default=12)
    args = parser.parse_args()

    rules = load_rules(args.rules)
    classifier = DBTableClassifier(rules, bit_count=args.bits)
    classifier.build()
    mismatches = []
    for i, packet in enumerate(iter_packets(args.trace, limit=args.samples), start=1):
        expected = linear_search(rules, packet)
        observed = classifier.search(packet)
        if expected != observed:
            mismatches.append((i, expected, observed))
            if len(mismatches) >= 10:
                break

    if mismatches:
        for row in mismatches:
            print(f"packet={row[0]} expected={row[1]} observed={row[2]}")
        raise SystemExit(1)
    print(f"validated {args.samples} packets against linear scan")


if __name__ == "__main__":
    main()
