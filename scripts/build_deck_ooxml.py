from __future__ import annotations

import html
import json
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile


ROOT = Path(__file__).resolve().parents[1]
SUMMARY = json.loads((ROOT / "results" / "dbtable_results.json").read_text(encoding="utf-8"))
OUT = ROOT / "deliverables" / "DBTable_Final_Project_Presentation.pptx"

EMU = 914400
SLIDE_W = int(13.333 * EMU)
SLIDE_H = int(7.5 * EMU)


def emu(v: float) -> int:
    return int(v * EMU)


def esc(v: str) -> str:
    return html.escape(str(v), quote=True)


def shape_text(
    sid: int,
    name: str,
    text: str,
    x: float,
    y: float,
    w: float,
    h: float,
    font_size: int = 18,
    color: str = "14213D",
    bold: bool = False,
    fill: str | None = None,
    line: str | None = None,
    align: str = "l",
) -> str:
    fill_xml = '<a:noFill/>' if fill is None else f'<a:solidFill><a:srgbClr val="{fill}"/></a:solidFill>'
    line_xml = '<a:ln><a:noFill/></a:ln>' if line is None else f'<a:ln w="9525"><a:solidFill><a:srgbClr val="{line}"/></a:solidFill></a:ln>'
    paras = []
    for raw in text.split("\n"):
        rpr = f'<a:rPr lang="zh-TW" sz="{font_size * 100}" dirty="0" smtClean="0">'
        if bold:
            rpr = f'<a:rPr lang="zh-TW" sz="{font_size * 100}" b="1" dirty="0" smtClean="0">'
        rpr += f'<a:solidFill><a:srgbClr val="{color}"/></a:solidFill><a:latin typeface="Microsoft JhengHei"/><a:ea typeface="Microsoft JhengHei"/></a:rPr>'
        paras.append(f'<a:p><a:pPr algn="{align}"/><a:r>{rpr}<a:t>{esc(raw)}</a:t></a:r></a:p>')
    return f"""
    <p:sp>
      <p:nvSpPr><p:cNvPr id="{sid}" name="{esc(name)}"/><p:cNvSpPr txBox="1"/><p:nvPr/></p:nvSpPr>
      <p:spPr>
        <a:xfrm><a:off x="{emu(x)}" y="{emu(y)}"/><a:ext cx="{emu(w)}" cy="{emu(h)}"/></a:xfrm>
        <a:prstGeom prst="roundRect"><a:avLst/></a:prstGeom>
        {fill_xml}{line_xml}
      </p:spPr>
      <p:txBody><a:bodyPr wrap="square" anchor="mid" lIns="45720" tIns="45720" rIns="45720" bIns="45720"/><a:lstStyle/>{''.join(paras)}</p:txBody>
    </p:sp>
    """


def line(sid: int, x: float, y: float, w: float, color: str = "2F9CBB") -> str:
    return f"""
    <p:cxnSp>
      <p:nvCxnSpPr><p:cNvPr id="{sid}" name="line {sid}"/><p:cNvCxnSpPr/><p:nvPr/></p:nvCxnSpPr>
      <p:spPr><a:xfrm><a:off x="{emu(x)}" y="{emu(y)}"/><a:ext cx="{emu(w)}" cy="0"/></a:xfrm>
      <a:prstGeom prst="line"><a:avLst/></a:prstGeom><a:ln w="19050"><a:solidFill><a:srgbClr val="{color}"/></a:solidFill></a:ln></p:spPr>
    </p:cxnSp>
    """


def slide_xml(title: str, kicker: str, body_shapes: list[str], page: int, dark: bool = False) -> str:
    bg = "14213D" if dark else "F7FAFC"
    shapes = [
        f'<p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr><p:grpSpPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="{SLIDE_W}" cy="{SLIDE_H}"/><a:chOff x="0" y="0"/><a:chExt cx="{SLIDE_W}" cy="{SLIDE_H}"/></a:xfrm></p:grpSpPr>'
    ]
    if title:
        shapes.append(shape_text(2, "kicker", kicker, 0.55, 0.3, 3.3, 0.32, 9, "2F9CBB", True, None, None))
        shapes.append(line(3, 0.55, 0.72, 1.0))
        shapes.append(shape_text(4, "title", title, 0.55, 0.82, 11.85, 0.78, 27, "14213D" if not dark else "FFFFFF", True, None, None))
    shapes.extend(body_shapes)
    shapes.append(shape_text(900, "footer", f"DBTable Packet Classification | {page}", 10.8, 7.06, 1.95, 0.18, 8, "7A8793" if not dark else "BFD8E5", False, None, None, "r"))
    return f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:sld xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"
       xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"
       xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main">
  <p:cSld>
    <p:bg><p:bgPr><a:solidFill><a:srgbClr val="{bg}"/></a:solidFill><a:effectLst/></p:bgPr></p:bg>
    <p:spTree>{''.join(shapes)}</p:spTree>
  </p:cSld>
  <p:clrMapOvr><a:masterClrMapping/></p:clrMapOvr>
</p:sld>"""


def bullets(items: list[str], x: float, y: float, w: float, h: float, sid: int) -> str:
    return shape_text(sid, "bullets", "\n".join(f"- {item}" for item in items), x, y, w, h, 16, "14213D", False, None, None)


def metric(sid: int, value: str, label: str, x: float, y: float, color: str = "1F4E79") -> str:
    return (
        shape_text(sid, "metric", value, x, y, 2.25, 0.48, 20, color, True, "FFFFFF", "D6DEE7", "ctr")
        + shape_text(sid + 1, "label", label, x, y + 0.48, 2.25, 0.46, 10, "52606D", False, "FFFFFF", "D6DEE7", "ctr")
    )


def simple_table(headers: list[str], rows: list[list[str]], x: float, y: float, w: float, row_h: float, sid: int) -> str:
    col_w = w / len(headers)
    out = []
    for i, head in enumerate(headers):
        out.append(shape_text(sid, "th", head, x + i * col_w, y, col_w, row_h, 10, "14213D", True, "E6F1F7", "A6B7C8"))
        sid += 1
    for r, row in enumerate(rows):
        for i, cell in enumerate(row):
            out.append(shape_text(sid, "td", cell, x + i * col_w, y + (r + 1) * row_h, col_w, row_h, 9, "14213D", False, "FFFFFF", "D5DEE8"))
            sid += 1
    return "".join(out)


def build_slides() -> list[str]:
    s: list[str] = []
    s.append(slide_xml("", "", [
        shape_text(10, "cover-title", "DBTable", 0.72, 0.85, 5.5, 0.75, 44, "FFFFFF", True, None, None),
        shape_text(11, "subtitle", "Leveraging discriminative bitsets for high-performance packet classification", 0.76, 1.68, 9.2, 0.46, 18, "D7E9F3", False, None, None),
        line(12, 0.78, 2.34, 3.0),
        metric(13, f"{SUMMARY['rules_loaded']:,}", "valid ClassBench ACL1 rules", 0.78, 5.2, "2F9CBB"),
        metric(15, f"{SUMMARY['lookup_avg_ns']:.0f} ns", "average lookup", 3.22, 5.2, "2F9CBB"),
        metric(17, f"{SUMMARY['estimated_memory_bytes'] / 1048576:.2f} MiB", "estimated memory", 5.66, 5.2, "2F9CBB"),
        shape_text(19, "author", "高效能網路期末專案 | P77141155 陳燁龍", 0.8, 6.9, 6.4, 0.24, 10, "BFD8E5", False, None, None),
    ], 1, True))

    s.append(slide_xml("本專案完成 DBTable 的研究、實作與實驗評估", "PROJECT SCOPE", [
        bullets([
            "研究 DBTable 如何以 discriminative bits 降低 packet lookup 候選集合",
            "下載 AMPS 參考實作與 ClassBench ACL1 100K rules/trace",
            "撰寫可重現的 DBTable-inspired Python classifier 與 benchmark",
            "量測 build time、lookup time、memory consumption，並提供組員比較框架",
        ], 0.8, 2.25, 11.3, 2.8, 20)
    ], 2))

    s.append(slide_xml("Packet classification 是最高優先權五元組匹配問題", "PROBLEM", [
        shape_text(20, "sip", "Source IP\nprefix", 0.8, 2.15, 1.75, 0.95, 14, "14213D", True, "FFFFFF", "A6B7C8", "ctr"),
        shape_text(21, "dip", "Destination IP\nprefix", 2.9, 2.15, 1.85, 0.95, 14, "14213D", True, "FFFFFF", "A6B7C8", "ctr"),
        shape_text(22, "sport", "Source Port\nrange", 5.1, 2.15, 1.75, 0.95, 14, "14213D", True, "FFFFFF", "A6B7C8", "ctr"),
        shape_text(23, "dport", "Destination Port\nrange", 7.2, 2.15, 1.95, 0.95, 14, "14213D", True, "FFFFFF", "A6B7C8", "ctr"),
        shape_text(24, "proto", "Protocol\nmask", 9.55, 2.15, 1.65, 0.95, 14, "14213D", True, "FFFFFF", "A6B7C8", "ctr"),
        shape_text(25, "desc", "封包到達時，需要在大量規則中找出所有匹配者，並回傳 priority 最高的 rule。困難點在於 IP prefix、port range 與 wildcard/mask 會讓搜尋空間快速膨脹。", 1.05, 4.1, 10.9, 0.9, 18, "14213D", False, None, None),
    ], 3))

    s.append(slide_xml("DBTable 用具辨識力的 bit 先縮小候選規則集合", "CORE IDEA", [
        bullets([
            "建表前分析 ruleset：哪些 IP bit 能把規則切得最平均、覆蓋率最高",
            "以 selected bits 形成 bucket key；規則被放到相容 bucket",
            "Lookup 時 packet 只需取同一組 bits 找 bucket，再做完整五元組驗證",
            "效果：把 full ruleset scan 轉成 candidate bucket scan",
        ], 0.75, 1.95, 5.55, 3.8, 20),
        shape_text(21, "full", "Full ruleset\n~99K rules", 7.0, 2.0, 1.8, 0.9, 14, "14213D", True, "FFF7E6", "A6B7C8", "ctr"),
        shape_text(22, "rank", "Bit ranking\n12 selected bits", 9.0, 2.0, 1.8, 0.9, 14, "14213D", True, "EAF7FA", "A6B7C8", "ctr"),
        shape_text(23, "buckets", "4096 buckets\navg 169 rules", 8.0, 3.55, 2.1, 0.95, 14, "14213D", True, "EDF7F1", "A6B7C8", "ctr"),
    ], 4))

    s.append(slide_xml("建表與查詢分成兩條清楚流程", "ARCHITECTURE", [
        shape_text(20, "r", "ClassBench\nrules", 0.75, 2.0, 1.55, 0.78, 13, "14213D", True, "FFFFFF", "A6B7C8", "ctr"),
        shape_text(21, "p", "Parser", 2.75, 2.0, 1.4, 0.78, 13, "14213D", True, "FFFFFF", "A6B7C8", "ctr"),
        shape_text(22, "b", "Bit ranking", 4.6, 2.0, 1.55, 0.78, 13, "14213D", True, "FFFFFF", "A6B7C8", "ctr"),
        shape_text(23, "bt", "Bucket table", 6.65, 2.0, 1.65, 0.78, 13, "14213D", True, "FFFFFF", "A6B7C8", "ctr"),
        shape_text(24, "tr", "Packet\ntrace", 0.75, 4.0, 1.55, 0.78, 13, "14213D", True, "FFF7E6", "A6B7C8", "ctr"),
        shape_text(25, "ke", "Key extraction", 2.75, 4.0, 1.55, 0.78, 13, "14213D", True, "FFF7E6", "A6B7C8", "ctr"),
        shape_text(26, "cb", "Candidate\nbucket", 4.85, 4.0, 1.6, 0.78, 13, "14213D", True, "FFF7E6", "A6B7C8", "ctr"),
        shape_text(27, "em", "Exact match\n+ priority", 7.0, 4.0, 1.8, 0.78, 13, "14213D", True, "FFF7E6", "A6B7C8", "ctr"),
    ], 5))

    s.append(slide_xml("建表成本主要來自 bit ranking 與 bucket replication", "BUILD PIPELINE", [
        simple_table(["Step", "Work", "Output"], [
            ["1", "Parse ClassBench rules", "Rule objects"],
            ["2", "Score each IP bit by split balance and coverage", "Selected bits"],
            ["3", "Generate compatible bucket keys for each rule", "Bucket table"],
            ["4", "Sort candidates by priority", "Fast lookup lists"],
        ], 0.8, 1.95, 11.4, 0.52, 20),
        metric(60, f"{SUMMARY['build_seconds']:.3f} s", "measured build time", 0.95, 5.55),
        metric(62, f"{SUMMARY['replicated_entries']:,}", "replicated bucket entries", 3.45, 5.55),
        metric(64, f"{SUMMARY['fallback_rules']}", "fallback rules", 5.95, 5.55),
    ], 6))

    s.append(slide_xml("查詢只掃描一個候選 bucket，再做精確五元組比對", "LOOKUP PIPELINE", [
        shape_text(20, "in", "Incoming packet", 0.95, 2.3, 1.8, 0.85, 13, "14213D", True, "EAF7FA", "A6B7C8", "ctr"),
        shape_text(21, "ex", "Extract selected\nIP bits", 3.15, 2.3, 1.85, 0.85, 13, "14213D", True, "EAF7FA", "A6B7C8", "ctr"),
        shape_text(22, "find", "Find candidate\nbucket", 5.45, 2.3, 1.85, 0.85, 13, "14213D", True, "EAF7FA", "A6B7C8", "ctr"),
        shape_text(23, "ver", "Verify 5-tuple\nconstraints", 7.75, 2.3, 1.95, 0.85, 13, "14213D", True, "EAF7FA", "A6B7C8", "ctr"),
        shape_text(24, "ret", "Return best\npriority", 10.15, 2.3, 1.65, 0.85, 13, "14213D", True, "EAF7FA", "A6B7C8", "ctr"),
        bullets(["候選 bucket 內仍做 exact match，因此分類結果可驗證", "若 selected bits 對資料集有辨識力，平均候選規則數會大幅下降", "Wildcard prefix 會造成規則複製，是 DBTable 記憶體與建表成本的重要來源"], 1.15, 4.35, 10.7, 1.45, 30),
    ], 7))

    s.append(slide_xml("本專案保留 DBTable 核心概念，並讓實驗可重現", "IMPLEMENTATION", [
        simple_table(["File", "Role"], [
            ["src/classbench.py", "Rule/trace parser and exact 5-tuple matcher"],
            ["src/dbtable_classifier.py", "Discriminative-bit bucket classifier"],
            ["scripts/run_experiment.py", "Build/lookup/memory benchmark"],
            ["scripts/validate_correctness.py", "Linear-scan oracle smoke test"],
        ], 0.75, 1.9, 11.8, 0.56, 20),
        shape_text(60, "limit", "Important limitation: this is a DBTable-inspired educational implementation, not a line-by-line port of the AMPS C++ version.", 0.95, 5.65, 11.2, 0.35, 14, "A23B3B", True, None, None),
    ], 8))

    s.append(slide_xml("ClassBench ACL1 100K rules 作為測試資料集", "DATASET", [
        metric(20, f"{SUMMARY['rules_loaded']:,}", "valid parsed rules", 0.9, 2.05),
        metric(22, f"{SUMMARY['packets_tested']:,}", "packets tested", 3.45, 2.05),
        metric(24, f"{SUMMARY['bucket_count']:,}", "buckets", 6.0, 2.05),
        metric(26, f"{SUMMARY['average_bucket_size']:.1f}", "avg bucket size", 8.55, 2.05),
        bullets(["資料來源已下載至 data/classbench/", "外部參考實作保留於 external/amps/", "ClassBench 100K 檔案實際可解析有效規則數為 99,330，報告中已明確記錄"], 1.0, 4.1, 10.8, 1.55, 30),
    ], 9))

    s.append(slide_xml("DBTable-inspired 實測結果顯示候選集合已有效縮小", "RESULTS", [
        metric(20, f"{SUMMARY['build_seconds']:.3f} s", "build time", 0.9, 2.05, "2E7D59"),
        metric(22, f"{SUMMARY['lookup_avg_ns']:.0f} ns", "average lookup", 3.45, 2.05, "2E7D59"),
        metric(24, f"{SUMMARY['lookup_p99_ns']:.0f} ns", "P99 lookup", 6.0, 2.05, "2E7D59"),
        metric(26, f"{SUMMARY['estimated_memory_bytes'] / 1048576:.2f} MiB", "estimated memory", 8.55, 2.05, "2E7D59"),
        bullets(["4096 buckets 將近十萬規則分散成平均約 169 筆的候選集合", "Lookup 成本主要由 candidate bucket scan 與 exact match 決定", "Correctness smoke test: 200 sampled packets matched linear scan oracle"], 1.0, 4.45, 10.8, 1.35, 30),
    ], 10))

    s.append(slide_xml("與組員演算法比較時，建議用同一組三個核心指標", "COMPARISON", [
        simple_table(["Dimension", "DBTable", "Group Algorithm A", "Group Algorithm B"], [
            ["Build", f"{SUMMARY['build_seconds']:.3f} s", "replace with teammate data", "replace with teammate data"],
            ["Lookup", f"{SUMMARY['lookup_avg_ns']:.0f} ns avg", "replace", "replace"],
            ["Memory", f"{SUMMARY['estimated_memory_bytes'] / 1048576:.2f} MiB", "replace", "replace"],
            ["Best fit", "IP bits are discriminative", "replace", "replace"],
        ], 0.65, 1.85, 12.0, 0.55, 20),
        shape_text(60, "note", "報告已放入可替換比較表；取得同組兩位數據後，直接更新 Algorithm A/B 欄位即可。", 0.9, 5.82, 11.0, 0.3, 14, "52606D", False, None, None),
    ], 11))

    s.append(slide_xml("DBTable 把 ruleset 分布轉成快速 bucket index", "CONCLUSION", [
        bullets([
            "優點：查詢候選集合小，對 ACL-like ruleset 的平均 lookup latency 有利",
            "代價：wildcard prefix 會造成 replication，完整最佳化實作比簡單 hash table 複雜",
            "本專案已完成 dataset、程式、benchmark、報告、PPT 與錄影講稿",
            "下一步：取得組員演算法與結果，完成正式比較分析表",
        ], 0.9, 2.0, 11.0, 3.2, 20),
    ], 12))
    return s


def write_static_files(z: ZipFile, slide_count: int) -> None:
    overrides = [
        '<Override PartName="/ppt/presentation.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.presentation.main+xml"/>',
        '<Override PartName="/ppt/slideMasters/slideMaster1.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slideMaster+xml"/>',
        '<Override PartName="/ppt/slideLayouts/slideLayout1.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slideLayout+xml"/>',
        '<Override PartName="/ppt/theme/theme1.xml" ContentType="application/vnd.openxmlformats-officedocument.theme+xml"/>',
        '<Override PartName="/docProps/core.xml" ContentType="application/vnd.openxmlformats-package.core-properties+xml"/>',
        '<Override PartName="/docProps/app.xml" ContentType="application/vnd.openxmlformats-officedocument.extended-properties+xml"/>',
    ]
    overrides += [f'<Override PartName="/ppt/slides/slide{i}.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slide+xml"/>' for i in range(1, slide_count + 1)]
    z.writestr("[Content_Types].xml", f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  {''.join(overrides)}
</Types>""")
    z.writestr("_rels/.rels", """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="ppt/presentation.xml"/>
  <Relationship Id="rId2" Type="http://schemas.openxmlformats.org/package/2006/relationships/metadata/core-properties" Target="docProps/core.xml"/>
  <Relationship Id="rId3" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/extended-properties" Target="docProps/app.xml"/>
</Relationships>""")
    z.writestr("docProps/core.xml", """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties" xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:dcterms="http://purl.org/dc/terms/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"><dc:title>DBTable Packet Classification</dc:title><dc:creator>Codex</dc:creator><cp:lastModifiedBy>Codex</cp:lastModifiedBy></cp:coreProperties>""")
    z.writestr("docProps/app.xml", f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Properties xmlns="http://schemas.openxmlformats.org/officeDocument/2006/extended-properties" xmlns:vt="http://schemas.openxmlformats.org/officeDocument/2006/docPropsVTypes"><Application>Codex</Application><PresentationFormat>Wide</PresentationFormat><Slides>{slide_count}</Slides></Properties>""")
    slide_ids = "".join([f'<p:sldId id="{255 + i}" r:id="rId{i + 1}"/>' for i in range(1, slide_count + 1)])
    z.writestr("ppt/presentation.xml", f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:presentation xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main">
  <p:sldMasterIdLst><p:sldMasterId id="2147483648" r:id="rId1"/></p:sldMasterIdLst>
  <p:sldIdLst>{slide_ids}</p:sldIdLst>
  <p:sldSz cx="{SLIDE_W}" cy="{SLIDE_H}" type="wide"/>
  <p:notesSz cx="6858000" cy="9144000"/>
</p:presentation>""")
    rels = ['<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideMaster" Target="slideMasters/slideMaster1.xml"/>']
    rels += [f'<Relationship Id="rId{i + 1}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slide" Target="slides/slide{i}.xml"/>' for i in range(1, slide_count + 1)]
    z.writestr("ppt/_rels/presentation.xml.rels", f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">{''.join(rels)}</Relationships>""")
    z.writestr("ppt/slideMasters/slideMaster1.xml", f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:sldMaster xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"><p:cSld><p:spTree><p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr><p:grpSpPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="{SLIDE_W}" cy="{SLIDE_H}"/><a:chOff x="0" y="0"/><a:chExt cx="{SLIDE_W}" cy="{SLIDE_H}"/></a:xfrm></p:grpSpPr></p:spTree></p:cSld><p:clrMap bg1="lt1" tx1="dk1" bg2="lt2" tx2="dk2" accent1="accent1" accent2="accent2" accent3="accent3" accent4="accent4" accent5="accent5" accent6="accent6" hlink="hlink" folHlink="folHlink"/><p:sldLayoutIdLst><p:sldLayoutId id="2147483649" r:id="rId1"/></p:sldLayoutIdLst><p:txStyles><p:titleStyle/><p:bodyStyle/><p:otherStyle/></p:txStyles></p:sldMaster>""")
    z.writestr("ppt/slideMasters/_rels/slideMaster1.xml.rels", """<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideLayout" Target="../slideLayouts/slideLayout1.xml"/><Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/theme" Target="../theme/theme1.xml"/></Relationships>""")
    z.writestr("ppt/slideLayouts/slideLayout1.xml", f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?><p:sldLayout xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main" type="blank"><p:cSld name="Blank"><p:spTree><p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr><p:grpSpPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="{SLIDE_W}" cy="{SLIDE_H}"/><a:chOff x="0" y="0"/><a:chExt cx="{SLIDE_W}" cy="{SLIDE_H}"/></a:xfrm></p:grpSpPr></p:spTree></p:cSld><p:clrMapOvr><a:masterClrMapping/></p:clrMapOvr></p:sldLayout>""")
    z.writestr("ppt/slideLayouts/_rels/slideLayout1.xml.rels", """<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideMaster" Target="../slideMasters/slideMaster1.xml"/></Relationships>""")
    z.writestr("ppt/theme/theme1.xml", """<?xml version="1.0" encoding="UTF-8" standalone="yes"?><a:theme xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" name="DBTable"><a:themeElements><a:clrScheme name="DBTable"><a:dk1><a:srgbClr val="14213D"/></a:dk1><a:lt1><a:srgbClr val="FFFFFF"/></a:lt1><a:dk2><a:srgbClr val="1F4E79"/></a:dk2><a:lt2><a:srgbClr val="F7FAFC"/></a:lt2><a:accent1><a:srgbClr val="2F9CBB"/></a:accent1><a:accent2><a:srgbClr val="2E7D59"/></a:accent2><a:accent3><a:srgbClr val="A23B3B"/></a:accent3><a:accent4><a:srgbClr val="52606D"/></a:accent4><a:accent5><a:srgbClr val="A6B7C8"/></a:accent5><a:accent6><a:srgbClr val="FFF7E6"/></a:accent6><a:hlink><a:srgbClr val="0563C1"/></a:hlink><a:folHlink><a:srgbClr val="954F72"/></a:folHlink></a:clrScheme><a:fontScheme name="Office"><a:majorFont><a:latin typeface="Microsoft JhengHei"/><a:ea typeface="Microsoft JhengHei"/></a:majorFont><a:minorFont><a:latin typeface="Microsoft JhengHei"/><a:ea typeface="Microsoft JhengHei"/></a:minorFont></a:fontScheme><a:fmtScheme name="Office"><a:fillStyleLst/><a:lnStyleLst/><a:effectStyleLst/><a:bgFillStyleLst/></a:fmtScheme></a:themeElements></a:theme>""")


def main() -> None:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    slides = build_slides()
    with ZipFile(OUT, "w", ZIP_DEFLATED) as z:
        write_static_files(z, len(slides))
        for i, xml in enumerate(slides, start=1):
            z.writestr(f"ppt/slides/slide{i}.xml", xml)
            z.writestr(f"ppt/slides/_rels/slide{i}.xml.rels", """<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideLayout" Target="../slideLayouts/slideLayout1.xml"/></Relationships>""")
    print(json.dumps({"pptx": str(OUT), "slides": len(slides), "bytes": OUT.stat().st_size}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
