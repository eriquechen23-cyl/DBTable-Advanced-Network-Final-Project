from __future__ import annotations

import csv
import json
from pathlib import Path
import statistics
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
EXE = ROOT / "results" / "benchmark_ta_dbtable.exe"
RULES = ROOT / "data" / "classbench" / "acl1_100000.txt"
TRACE = ROOT / "data" / "classbench" / "acl1_100000.txt_trace"
OUT_JSON = ROOT / "results" / "ta_dbtable_results.json"
OUT_CSV = ROOT / "results" / "ta_dbtable_results.csv"


def run_cmd(cmd: list[str]) -> str:
    completed = subprocess.run(
        cmd,
        cwd=ROOT,
        check=True,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    return completed.stdout


def compile_benchmark() -> None:
    cmd = [
        "g++",
        "-std=c++17",
        "-O3",
        "-mbmi2",
        "-I",
        "ta_reference/amps_dbtable/include",
        "-I",
        "ta_reference/amps_dbtable/include",
        "cpp/benchmark_ta_dbtable.cpp",
        "ta_reference/amps_dbtable/DBTable.cpp",
        "-o",
        str(EXE),
    ]
    run_cmd(cmd)


def parse_json_from_output(output: str) -> dict:
    start = output.find("{")
    end = output.rfind("}")
    if start < 0 or end < start:
        raise ValueError(f"No JSON object found in output:\n{output}")
    return json.loads(output[start : end + 1])


def main() -> None:
    repeats = int(sys.argv[1]) if len(sys.argv) > 1 else 5
    packets = int(sys.argv[2]) if len(sys.argv) > 2 else 100000
    threshold = int(sys.argv[3]) if len(sys.argv) > 3 else 4
    compile_benchmark()

    runs = []
    for _ in range(repeats):
        output = run_cmd([str(EXE), str(RULES), str(TRACE), str(packets), str(threshold)])
        runs.append(parse_json_from_output(output))

    summary = {
        "implementation": "AMPS/TA DBTable.cpp",
        "source_file": "ta_reference/amps_dbtable/DBTable.cpp",
        "rules_file": str(RULES),
        "trace_file": str(TRACE),
        "repeats": repeats,
        "rules_loaded": runs[0]["rules_loaded"],
        "packets_tested": runs[0]["packets_tested"],
        "matched_packets": runs[0]["matched_packets"],
        "threshold": threshold,
        "build_seconds_avg": statistics.fmean(r["build_seconds"] for r in runs),
        "build_seconds_min": min(r["build_seconds"] for r in runs),
        "lookup_avg_ns_avg": statistics.fmean(r["lookup_avg_ns"] for r in runs),
        "lookup_avg_ns_min": min(r["lookup_avg_ns"] for r in runs),
        "lookup_total_seconds_avg": statistics.fmean(r["lookup_total_seconds"] for r in runs),
        "estimated_memory_bytes": runs[0]["estimated_memory_bytes"],
        "estimated_memory_mib": runs[0]["estimated_memory_mib"],
        "runs": runs,
    }

    OUT_JSON.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    with OUT_CSV.open("w", newline="", encoding="utf-8") as fh:
        fields = [key for key, value in summary.items() if key != "runs"]
        writer = csv.DictWriter(fh, fieldnames=fields)
        writer.writeheader()
        writer.writerow({key: summary[key] for key in fields})
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
