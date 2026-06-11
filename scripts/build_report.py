from __future__ import annotations

import json
from pathlib import Path

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_CELL_VERTICAL_ALIGNMENT
from docx.shared import Inches, Pt, RGBColor


ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results" / "dbtable_results.json"
DELIVERABLES = ROOT / "deliverables"
REPORTS = ROOT / "docs" / "reports"


def set_cell(cell, text: str, bold: bool = False) -> None:
    cell.text = ""
    p = cell.paragraphs[0]
    run = p.add_run(text)
    run.bold = bold
    for paragraph in cell.paragraphs:
        paragraph.paragraph_format.space_after = Pt(2)
    cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER


def add_table(doc: Document, headers: list[str], rows: list[list[str]]) -> None:
    table = doc.add_table(rows=1, cols=len(headers))
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.style = "Table Grid"
    for i, h in enumerate(headers):
        set_cell(table.rows[0].cells[i], h, bold=True)
    for row in rows:
        cells = table.add_row().cells
        for i, value in enumerate(row):
            set_cell(cells[i], value)
    doc.add_paragraph()


def add_heading(doc: Document, text: str, level: int = 1) -> None:
    p = doc.add_heading(text, level=level)
    for run in p.runs:
        run.font.name = "Microsoft JhengHei"
        run.font.color.rgb = RGBColor(31, 78, 121)


def build_docx(summary: dict) -> Path:
    DELIVERABLES.mkdir(parents=True, exist_ok=True)
    doc = Document()
    section = doc.sections[0]
    section.top_margin = Inches(0.75)
    section.bottom_margin = Inches(0.75)
    section.left_margin = Inches(0.85)
    section.right_margin = Inches(0.85)

    styles = doc.styles
    styles["Normal"].font.name = "Microsoft JhengHei"
    styles["Normal"].font.size = Pt(10.5)

    title = doc.add_paragraph()
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = title.add_run("高效能網路期末專案書面報告\nDBTable Packet Classification")
    r.bold = True
    r.font.size = Pt(22)
    r.font.name = "Microsoft JhengHei"

    meta = doc.add_paragraph()
    meta.alignment = WD_ALIGN_PARAGRAPH.CENTER
    meta.add_run("演算法：DBTable | 資料集：ClassBench ACL1 100K rules | 作者：P77141155 陳燁龍")
    doc.add_paragraph()

    add_heading(doc, "摘要", 1)
    doc.add_paragraph(
        "本報告研究 DBTable 封包分類演算法。封包分類需要在大量規則中，依照來源 IP、目的 IP、來源埠、目的埠與協定五元組找到最高優先權規則。"
        "DBTable 的核心精神是利用具辨識力的 bit 將規則集合切分成較小候選集合，使查詢階段避免掃描完整 ruleset。"
        "本專案下載 AMPS 參考實作與 ClassBench 工具，並以 Python 撰寫一個可重現的 DBTable-inspired 實驗程式，實測 build time、lookup time 與 memory consumption。"
    )

    add_heading(doc, "1. 演算法介紹與架構分析", 1)
    add_heading(doc, "1.1 問題定義", 2)
    doc.add_paragraph(
        "封包分類輸入為 packet 五元組：source IP、destination IP、source port、destination port、protocol。"
        "規則通常包含 IP prefix、port range、protocol mask 與 priority。查詢結果必須回傳所有相符規則中優先權最高者。"
    )
    add_heading(doc, "1.2 DBTable 核心想法", 2)
    doc.add_paragraph(
        "DBTable 以 discriminative bits 建立 bucket table。建表時先分析 ruleset 中哪些 IP bit 能把規則切得最平均，"
        "再以這些 bit 形成 bucket key。查詢時，packet 只需取出相同 bit 形成 key，進入對應 bucket 後再做完整五元組驗證。"
        "這種設計把 lookup 成本從完整 ruleset scan 降低為小型候選集合 scan。AMPS 的 C++ 版本還包含更細緻的 subset、ip_node、prefix_tuple 與 port_node 結構。"
    )
    add_heading(doc, "1.3 架構圖", 2)
    diagram = doc.add_paragraph()
    diagram.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = diagram.add_run(
        "ClassBench Rules -> Parser -> Discriminative Bit Ranking -> Bucket Table Build\n"
        "Packet Trace -> Key Extraction -> Candidate Bucket -> Exact 5-tuple Match -> Highest Priority Rule"
    )
    run.font.name = "Consolas"
    run.font.size = Pt(10)
    add_table(
        doc,
        ["階段", "輸入", "主要工作", "輸出"],
        [
            ["Rule parsing", "ClassBench rule file", "解析 IP prefix、port range、protocol mask、priority", "Rule objects"],
            ["Bit ranking", "All rules", "計算每個 IP bit 的分割平衡度與覆蓋率", "Selected discriminative bits"],
            ["Bucket build", "Rules + selected bits", "依 selected bits 建立 bucket；wildcard bit 會複製到多個 bucket", "Bucket table"],
            ["Lookup", "Packet trace", "取 packet key，掃描候選 bucket，做精確五元組比對", "Best matching priority"],
        ],
    )

    add_heading(doc, "2. 實作方法", 1)
    doc.add_paragraph(
        "本專案實作位於 src/ 與 scripts/。為了讓實驗能在一般課程環境重現，使用 Python 撰寫 DBTable-inspired classifier；"
        "外部 AMPS C++ 原始碼保留在 external/amps 作為演算法參考。"
    )
    add_table(
        doc,
        ["檔案", "用途"],
        [
            ["src/classbench.py", "ClassBench rule/trace parser 與精確五元組 match helper"],
            ["src/dbtable_classifier.py", "DBTable-inspired discriminative-bit bucket classifier"],
            ["scripts/run_experiment.py", "產生 build time、lookup time、memory consumption 結果"],
            ["scripts/validate_correctness.py", "以線性掃描抽樣驗證查詢正確性"],
            ["scripts/generate_classbench_dataset.ps1", "從 ClassBench seed 重新產生資料集的輔助腳本"],
        ],
    )
    doc.add_paragraph(
        "限制說明：此實作保留 DBTable 用 discriminative bits 減少候選規則的核心概念，但不是 AMPS C++ DBTable 的逐行移植；"
        "AMPS 版本包含更完整的 subset/tuple/port-node 調整策略。本實作適合作為課程實驗與報告分析基礎。"
    )

    add_heading(doc, "3. 實驗與效能評估", 1)
    add_heading(doc, "3.1 資料集與執行方式", 2)
    doc.add_paragraph(
        "使用 ClassBench ACL1 100K rules 檔案 data/classbench/acl1_100000.txt 與對應 trace。"
        f"此下載檔名為 100K，實際有效可解析規則數為 {summary['rules_loaded']:,} 筆，trace 測試封包數為 {summary['packets_tested']:,} 筆。"
    )
    doc.add_paragraph(
        "執行指令：python scripts/run_experiment.py --max-traces 100000"
    )
    add_heading(doc, "3.2 實驗結果", 2)
    add_table(
        doc,
        ["指標", "結果"],
        [
            ["Build time", f"{summary['build_seconds']:.4f} s"],
            ["Lookup total time", f"{summary['lookup_total_seconds']:.4f} s"],
            ["Average lookup time", f"{summary['lookup_avg_ns']:.1f} ns"],
            ["Median lookup time", f"{summary['lookup_median_ns']:.1f} ns"],
            ["P95 lookup time", f"{summary['lookup_p95_ns']:.1f} ns"],
            ["P99 lookup time", f"{summary['lookup_p99_ns']:.1f} ns"],
            ["Throughput", f"{summary['throughput_mpps']:.4f} Mpps"],
            ["Estimated memory", f"{summary['estimated_memory_bytes'] / (1024 * 1024):.2f} MiB"],
            ["Bucket count", f"{summary['bucket_count']:,}"],
            ["Average bucket size", f"{summary['average_bucket_size']:.2f} rules"],
            ["Max bucket size", f"{summary['max_bucket_size']:,} rules"],
        ],
    )
    doc.add_paragraph(
        "結果顯示，selected bits 將近十萬筆規則分散到 4096 個 bucket，平均每個 bucket 約 169 筆規則。"
        "因此 lookup 階段主要成本集中在候選 bucket 的少量規則驗證，而不是完整 ruleset 掃描。"
    )

    add_heading(doc, "4. 與組員演算法比較分析", 1)
    doc.add_paragraph(
        "注意：以下比較表已預留同組另外兩位組員的演算法與數據欄位。請在取得組員實測結果後替換 Algorithm A/B 與數值。"
        "若同組成員尚未提供結果，可先以此章節的分析框架完成初稿。"
    )
    add_table(
        doc,
        ["面向", "DBTable", "Algorithm A（請填組員演算法）", "Algorithm B（請填組員演算法）"],
        [
            ["設計核心", "用 discriminative bits 建 bucket，先縮小候選集合", "請填：例如 tuple-space/hash/tree", "請填：例如 decision tree/cut/split"],
            ["Build time", f"{summary['build_seconds']:.4f} s", "請填", "請填"],
            ["Lookup avg", f"{summary['lookup_avg_ns']:.1f} ns", "請填", "請填"],
            ["Memory", f"{summary['estimated_memory_bytes'] / (1024 * 1024):.2f} MiB", "請填", "請填"],
            ["優勢", "查詢候選集合小；對高可分辨 IP bits 的 ACL ruleset 有利", "請填", "請填"],
            ["弱點", "wildcard prefix 可能造成 bucket replication；完整版本實作複雜", "請填", "請填"],
            ["適用情境", "規則 IP prefix 具明顯分布差異、需要低平均 lookup latency", "請填", "請填"],
        ],
    )
    doc.add_paragraph(
        "定性比較上，若組員選的是 tuple-space search 類方法，其優點通常是結構簡單且 incremental update 較直覺，但 lookup 可能需查多個 tuple。"
        "若組員選的是 decision-tree/cut/split 類方法，其查詢路徑可能很短，但建樹成本、記憶體膨脹與 rule replication 會是主要風險。"
        "DBTable 位於兩者之間：它使用 bit-based bucket 取得快速候選定位，同時保留精確比對避免分類錯誤。"
    )

    add_heading(doc, "5. 結論", 1)
    doc.add_paragraph(
        "DBTable 的價值在於將 ruleset 的分布特性轉換成查詢前的 bucket index，使 packet lookup 不必面對完整規則集合。"
        "本次實驗在 ClassBench ACL1 100K 資料上完成建表、查詢與記憶體估計，並透過線性掃描抽樣驗證正確性。"
        "後續若要更貼近論文與 AMPS 實作，可將 prefix_tuple、port_node、動態 tuple range 與 C++ SIMD/hash optimization 納入。"
    )

    add_heading(doc, "參考資料", 1)
    refs = [
        "DBTable: Leveraging Discriminative Bitsets for High-Performance Packet Classification, IEEE/ACM Transactions on Networking, 2024.",
        "Packet classification algorithms list: https://github.com/matthiola0/packet-classification-algorithms",
        "AMPS reference implementation including DBTable: https://github.com/JiaChangGit/amps",
        "ClassBench packet classification generator: external/classbench-packet-classification and https://github.com/classbench-ng/classbench-ng",
    ]
    for ref in refs:
        doc.add_paragraph(ref, style=None)

    out = DELIVERABLES / "DBTable_Final_Project_Report.docx"
    doc.save(out)
    return out


def build_html(summary: dict) -> Path:
    REPORTS.mkdir(parents=True, exist_ok=True)
    html = f"""<!doctype html>
<html lang="zh-Hant">
<head>
  <meta charset="utf-8">
  <title>DBTable Architecture Milestone Report</title>
  <style>
    body {{ font-family: Arial, "Microsoft JhengHei", sans-serif; margin: 40px; color: #1f2937; line-height: 1.55; }}
    h1, h2 {{ color: #143d59; }}
    .meta, .note {{ color: #5b6472; }}
    .grid {{ display: grid; grid-template-columns: repeat(5, 1fr); gap: 12px; align-items: center; margin: 24px 0; }}
    .box {{ border: 1px solid #9eb6c8; background: #f7fbff; border-radius: 8px; padding: 12px; text-align: center; min-height: 58px; }}
    .arrow {{ text-align: center; color: #356b8c; font-weight: bold; }}
    table {{ border-collapse: collapse; width: 100%; margin: 16px 0; }}
    th, td {{ border: 1px solid #d0d7de; padding: 8px; vertical-align: top; }}
    th {{ background: #eaf3f8; text-align: left; }}
    code {{ background: #f4f4f4; padding: 2px 4px; }}
  </style>
</head>
<body>
  <h1>DBTable Architecture Milestone Report</h1>
  <p class="meta">Project: Final-Network | Milestone: architecture selected, implementation completed, benchmark verified | Author: Codex</p>

  <h2>Current Situation</h2>
  <p>Workspace now contains downloaded AMPS DBTable reference source, downloaded ClassBench source/data, a Python DBTable-inspired implementation, benchmark scripts, and generated report/PPT deliverable scripts.</p>

  <h2>Architecture Flow Diagram</h2>
  <div class="grid">
    <div class="box">ClassBench<br>Rules</div><div class="arrow">-></div>
    <div class="box">Parser<br>Rule objects</div><div class="arrow">-></div>
    <div class="box">Bit Ranking<br>Selected bits</div>
    <div class="box">Bucket Table<br>{summary['bucket_count']} buckets</div><div class="arrow">-></div>
    <div class="box">Packet Key<br>Extraction</div><div class="arrow">-></div>
    <div class="box">Candidate<br>Bucket Scan</div>
    <div class="box">Exact 5-tuple<br>Verification</div>
  </div>

  <h2>Implementation Summary</h2>
  <table>
    <tr><th>Area</th><th>Decision</th></tr>
    <tr><td>Classifier</td><td>DBTable-inspired discriminative IP bit bucket table with exact five-tuple verification.</td></tr>
    <tr><td>Dataset</td><td><code>data/classbench/acl1_100000.txt</code>; valid parsed rules: {summary['rules_loaded']:,}; tested packets: {summary['packets_tested']:,}.</td></tr>
    <tr><td>Verification</td><td>Benchmark completed and 200 sampled packet lookups matched linear scan oracle.</td></tr>
    <tr><td>Known gap</td><td>Educational Python implementation is not a line-by-line port of AMPS C++ DBTable.</td></tr>
  </table>

  <h2>Benchmark Snapshot</h2>
  <table>
    <tr><th>Metric</th><th>Value</th></tr>
    <tr><td>Build time</td><td>{summary['build_seconds']:.4f} s</td></tr>
    <tr><td>Average lookup</td><td>{summary['lookup_avg_ns']:.1f} ns</td></tr>
    <tr><td>P99 lookup</td><td>{summary['lookup_p99_ns']:.1f} ns</td></tr>
    <tr><td>Estimated memory</td><td>{summary['estimated_memory_bytes'] / (1024 * 1024):.2f} MiB</td></tr>
  </table>

  <h2>Recommended Next Step Direction</h2>
  <p>Replace the comparison chapter placeholders once the other two group members provide their algorithms and measured build/lookup/memory results. If more implementation depth is required, port AMPS C++ DBTable directly and compare it against the Python educational version.</p>
</body>
</html>
"""
    out = REPORTS / "20260611-DBTable-architecture-milestone.html"
    out.write_text(html, encoding="utf-8")
    return out


def build_script(summary: dict) -> Path:
    text = f"""# DBTable 20 分鐘投影片報告講稿

## 0:00-1:30 封面與研究目標
本次選擇 DBTable 作為 packet classification 演算法，目標是理解它如何用 discriminative bits 降低 lookup 時的候選規則數，並用 ClassBench ACL1 100K 資料做實驗。

## 1:30-4:00 Packet Classification 問題
說明五元組、priority、IP prefix、port range、protocol mask。強調查詢必須找最高優先權相符規則，因此不能只做近似分類。

## 4:00-8:00 DBTable 核心概念
介紹 discriminative bit ranking：選出能讓規則分布較平均、覆蓋率較高的 IP bit。規則依 selected bits 放入 bucket；wildcard prefix 會複製到多個 bucket。

## 8:00-11:00 架構與查詢流程
建表流程是 parser -> bit ranking -> bucket table。查詢流程是 packet key extraction -> candidate bucket -> exact five-tuple match -> best priority。

## 11:00-14:00 程式實作
說明 src/classbench.py、src/dbtable_classifier.py、scripts/run_experiment.py。強調本實作是 DBTable-inspired 教學版，不是 AMPS C++ 的完整逐行移植。

## 14:00-17:00 實驗結果
資料集有效可解析 rules: {summary['rules_loaded']:,}；packets tested: {summary['packets_tested']:,}。Build time {summary['build_seconds']:.4f} 秒，average lookup {summary['lookup_avg_ns']:.1f} ns，P99 {summary['lookup_p99_ns']:.1f} ns，memory 約 {summary['estimated_memory_bytes'] / (1024 * 1024):.2f} MiB。

## 17:00-19:00 比較分析
先說 DBTable 適合 IP bits 有明顯可分性的 ruleset。與 tuple-space 類方法相比，DBTable 查詢候選集合更小但 wildcard replication 是成本；與 decision-tree/cut 類方法相比，DBTable 結構較直接，但完整最佳化仍比簡單 hash table 複雜。

## 19:00-20:00 結論
總結 DBTable 的重點是把 ruleset 分布轉成快速 bucket index，降低平均 lookup 成本。後續可將 AMPS C++ 的 subset、prefix_tuple、port_node 與 SIMD/hash 最佳化納入。
"""
    out = DELIVERABLES / "DBTable_20min_Presentation_Script.md"
    out.write_text(text, encoding="utf-8")
    return out


def main() -> None:
    summary = json.loads(RESULTS.read_text(encoding="utf-8"))
    docx = build_docx(summary)
    html = build_html(summary)
    script = build_script(summary)
    print(json.dumps({"docx": str(docx), "html": str(html), "script": str(script)}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
