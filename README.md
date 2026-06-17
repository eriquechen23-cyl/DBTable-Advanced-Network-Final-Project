# DBTable Packet Classification Final Project

This workspace contains a reproducible coursework implementation and deliverables for the DBTable packet classification topic.

## Contents

- `data/classbench/acl1_100000.txt`: ClassBench ACL1 ruleset with 100K rules.
- `data/classbench/acl1_100000.txt_trace`: Matching ClassBench trace file.
- `src/classbench.py`: parser and exact five-tuple match helpers.
- `src/dbtable_classifier.py`: DBTable-inspired classifier using discriminative IP bit buckets.
- `scripts/run_experiment.py`: benchmark runner for build time, lookup time, and memory estimate.
- `scripts/build_report.py`: generates the DOCX written report, milestone HTML, and 20-minute script.
- `scripts/build_deck_ooxml.py`: generates the editable PPTX deck directly as OOXML.
- `scripts/run_ta_dbtable_experiment.py`: compiles and runs the AMPS/TA `DBTable.cpp` benchmark.
- `cpp/benchmark_ta_dbtable.cpp`: C++ harness for ClassBench rules/trace and AMPS DBTable.
- `external/amps`: downloaded AMPS reference source that includes the C++ DBTable implementation.
- `external/classbench-packet-classification`: downloaded ClassBench generator and seed files.

## Run

```powershell
$py = "C:\Users\jr008\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"
& $py scripts\run_experiment.py --max-traces 20000
```

For a full trace run, remove or raise `--max-traces`.

Run the AMPS/TA DBTable C++ benchmark used for the final report:

```powershell
& $py scripts\run_ta_dbtable_experiment.py 5 100000 4
```

Generate deliverables:

```powershell
& $py scripts\build_report.py
& $py scripts\build_deck_ooxml.py
```

## Dataset

The required 100K ClassBench rules are already copied to `data/classbench/`. To regenerate from the ClassBench seed files, use:

```powershell
.\scripts\generate_classbench_dataset.ps1
```

The generation script expects a working C/C++ build environment with `make`.
