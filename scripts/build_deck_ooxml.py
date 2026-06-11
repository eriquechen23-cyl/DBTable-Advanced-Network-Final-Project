from __future__ import annotations

import html
import json
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile


ROOT = Path(__file__).resolve().parents[1]
SUMMARY = json.loads((ROOT / "results" / "dbtable_results.json").read_text(encoding="utf-8"))
OUT = ROOT / "deliverables" / "DBTable_Final_Project_Presentation.pptx"
STUDENT = "P77141155 陳燁龍"

EMU = 914400
SLIDE_W = int(13.333 * EMU)
SLIDE_H = int(7.5 * EMU)


def emu(value: float) -> int:
    return int(value * EMU)


def esc(value: str) -> str:
    return html.escape(str(value), quote=True)


def text_box(
    sid: int,
    text: str,
    x: float,
    y: float,
    w: float,
    h: float,
    size: int = 18,
    color: str = "14213D",
    bold: bool = False,
    fill: str | None = None,
    line: str | None = None,
    align: str = "l",
    name: str = "text",
) -> str:
    fill_xml = '<a:noFill/>' if fill is None else f'<a:solidFill><a:srgbClr val="{fill}"/></a:solidFill>'
    line_xml = '<a:ln><a:noFill/></a:ln>' if line is None else f'<a:ln w="9525"><a:solidFill><a:srgbClr val="{line}"/></a:solidFill></a:ln>'
    paras = []
    for raw in text.split("\n"):
        bold_attr = ' b="1"' if bold else ""
        paras.append(
            f'<a:p><a:pPr algn="{align}"/><a:r>'
            f'<a:rPr lang="zh-TW" sz="{size * 100}"{bold_attr}>'
            f'<a:solidFill><a:srgbClr val="{color}"/></a:solidFill>'
            f'<a:latin typeface="Microsoft JhengHei"/><a:ea typeface="Microsoft JhengHei"/>'
            f'</a:rPr><a:t>{esc(raw)}</a:t></a:r></a:p>'
        )
    return f"""
    <p:sp>
      <p:nvSpPr><p:cNvPr id="{sid}" name="{esc(name)}"/><p:cNvSpPr txBox="1"/><p:nvPr/></p:nvSpPr>
      <p:spPr>
        <a:xfrm><a:off x="{emu(x)}" y="{emu(y)}"/><a:ext cx="{emu(w)}" cy="{emu(h)}"/></a:xfrm>
        <a:prstGeom prst="roundRect"><a:avLst/></a:prstGeom>
        {fill_xml}{line_xml}
      </p:spPr>
      <p:txBody><a:bodyPr wrap="square" anchor="mid" lIns="60960" tIns="60960" rIns="60960" bIns="60960"/><a:lstStyle/>{''.join(paras)}</p:txBody>
    </p:sp>
    """


def rule(sid: int, x: float, y: float, w: float, color: str = "2F9CBB") -> str:
    return f"""
    <p:cxnSp>
      <p:nvCxnSpPr><p:cNvPr id="{sid}" name="rule {sid}"/><p:cNvCxnSpPr/><p:nvPr/></p:nvCxnSpPr>
      <p:spPr><a:xfrm><a:off x="{emu(x)}" y="{emu(y)}"/><a:ext cx="{emu(w)}" cy="0"/></a:xfrm>
      <a:prstGeom prst="line"><a:avLst/></a:prstGeom><a:ln w="19050"><a:solidFill><a:srgbClr val="{color}"/></a:solidFill></a:ln></p:spPr>
    </p:cxnSp>
    """


def bullets(items: list[str], x: float, y: float, w: float, h: float, sid: int, size: int = 16) -> str:
    return text_box(sid, "\n".join(f"- {item}" for item in items), x, y, w, h, size=size)


def metric(sid: int, value: str, label: str, x: float, y: float, color: str = "1F4E79") -> str:
    return (
        text_box(sid, value, x, y, 2.35, 0.5, size=20, color=color, bold=True, fill="FFFFFF", line="D6DEE7", align="ctr", name="metric")
        + text_box(sid + 1, label, x, y + 0.48, 2.35, 0.45, size=10, color="52606D", fill="FFFFFF", line="D6DEE7", align="ctr", name="metric-label")
    )


def table(headers: list[str], rows: list[list[str]], x: float, y: float, w: float, row_h: float, sid: int) -> str:
    col_w = w / len(headers)
    parts: list[str] = []
    for i, header in enumerate(headers):
        parts.append(text_box(sid, header, x + i * col_w, y, col_w, row_h, size=10, bold=True, fill="E6F1F7", line="A6B7C8"))
        sid += 1
    for r, row in enumerate(rows):
        for i, cell in enumerate(row):
            parts.append(text_box(sid, cell, x + i * col_w, y + (r + 1) * row_h, col_w, row_h, size=9, fill="FFFFFF", line="D5DEE8"))
            sid += 1
    return "".join(parts)


def slide(title: str, kicker: str, body: list[str], page: int, dark: bool = False) -> str:
    bg = "14213D" if dark else "F7FAFC"
    shapes = [
        f'<p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr><p:grpSpPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="{SLIDE_W}" cy="{SLIDE_H}"/><a:chOff x="0" y="0"/><a:chExt cx="{SLIDE_W}" cy="{SLIDE_H}"/></a:xfrm></p:grpSpPr>'
    ]
    if title:
        title_color = "FFFFFF" if dark else "14213D"
        shapes.append(text_box(2, kicker, 0.55, 0.32, 4.0, 0.3, size=9, color="2F9CBB", bold=True))
        shapes.append(rule(3, 0.55, 0.72, 1.0))
        shapes.append(text_box(4, title, 0.55, 0.85, 11.9, 0.78, size=27, color=title_color, bold=True))
    shapes.extend(body)
    shapes.append(text_box(900, f"DBTable Packet Classification | {page}", 10.7, 7.05, 2.0, 0.2, size=8, color="BFD8E5" if dark else "7A8793", align="r"))
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


def build_slides() -> list[str]:
    slides: list[str] = []
    slides.append(
        slide(
            "",
            "",
            [
                text_box(10, "DBTable", 0.72, 0.85, 5.8, 0.8, size=44, color="FFFFFF", bold=True),
                text_box(11, "用 discriminative bitsets 加速 packet classification", 0.76, 1.72, 8.8, 0.45, size=20, color="D7E9F3"),
                rule(12, 0.78, 2.35, 3.0),
                metric(13, f"{SUMMARY['rules_loaded']:,}", "valid ClassBench ACL1 rules", 0.78, 5.2, "2F9CBB"),
                metric(15, f"{SUMMARY['lookup_avg_ns']:.0f} ns", "average lookup", 3.28, 5.2, "2F9CBB"),
                metric(17, f"{SUMMARY['estimated_memory_bytes'] / 1048576:.2f} MiB", "estimated memory", 5.78, 5.2, "2F9CBB"),
                text_box(19, f"高效能網路期末專案 | {STUDENT}", 0.8, 6.9, 6.6, 0.25, size=10, color="BFD8E5"),
            ],
            1,
            True,
        )
    )

    slides.append(
        slide(
            "封包分類其實是在大量規則中找最高優先權答案",
            "PROBLEM",
            [
                text_box(20, "封包五元組\nsource IP / destination IP\nsource port / destination port\nprotocol", 0.8, 2.0, 3.2, 1.4, size=17, bold=True, fill="FFFFFF", line="A6B7C8", align="ctr"),
                text_box(21, "規則條件\nIP prefix\nport range\nprotocol mask\npriority", 5.0, 2.0, 3.0, 1.4, size=17, bold=True, fill="FFFFFF", line="A6B7C8", align="ctr"),
                text_box(22, "查詢目標\n找出所有匹配規則中\npriority 最高者", 9.0, 2.0, 2.8, 1.4, size=17, bold=True, fill="FFFFFF", line="A6B7C8", align="ctr"),
                text_box(23, "困難點：規則數可能非常大，若每個封包都掃完整 ruleset，lookup latency 會隨規則數成長。DBTable 的目的就是先縮小候選規則集合。", 1.0, 4.55, 11.1, 0.8, size=19, fill="FFF7E6", line="E0C98F"),
            ],
            2,
        )
    )

    slides.append(
        slide(
            "白話版：DBTable 像圖書館索引，不是一本一本找",
            "PLAIN LANGUAGE",
            [
                text_box(20, "沒有索引", 0.9, 2.1, 2.2, 0.55, size=18, bold=True, fill="FDECEC", line="DDAAAA", align="ctr"),
                text_box(21, "封包來了就從第 1 條規則掃到最後一條。\n規則越多，查詢越慢。", 0.9, 2.85, 3.2, 1.1, size=15, fill="FFFFFF", line="DDAAAA"),
                text_box(22, "DBTable 的索引", 5.0, 2.1, 2.4, 0.55, size=18, bold=True, fill="EAF7FA", line="9CCBD8", align="ctr"),
                text_box(23, "先挑出最能分辨規則的 bit，做成 bucket table。\n封包先查索引，再進小 bucket 比對。", 5.0, 2.85, 3.4, 1.1, size=15, fill="FFFFFF", line="9CCBD8"),
                text_box(24, "結果", 9.6, 2.1, 1.8, 0.55, size=18, bold=True, fill="EDF7F1", line="9FC8AE", align="ctr"),
                text_box(25, "不是少做正確性檢查，\n而是少看不相關的規則。", 9.15, 2.85, 2.6, 1.1, size=15, fill="FFFFFF", line="9FC8AE", align="ctr"),
                text_box(26, "一句話：先用有辨識力的 bit 快速定位候選 bucket，再用完整五元組驗證正確答案。", 1.2, 5.0, 10.8, 0.55, size=20, color="1F4E79", bold=True, fill="FFFFFF", line="D6DEE7", align="ctr"),
            ],
            3,
        )
    )

    slides.append(
        slide(
            "DBTable 方法可以拆成四個步驟",
            "METHOD",
            [
                table(
                    ["Step", "白話意思", "技術意義"],
                    [
                        ["1", "觀察所有規則，看哪些 IP bit 最能分群。", "統計 bit 的分割平衡度與覆蓋率。"],
                        ["2", "挑出最有辨識力的 bit。", "形成 discriminative bitset。"],
                        ["3", "依這些 bit 把規則放進 bucket。", "wildcard prefix 會複製到多個 bucket。"],
                        ["4", "封包先找 bucket，再完整比對。", "exact match + highest priority。"],
                    ],
                    0.65,
                    1.9,
                    12.0,
                    0.68,
                    20,
                )
            ],
            4,
        )
    )

    slides.append(
        slide(
            "為什麼會快：把十萬筆規則縮成一個候選 bucket",
            "WHY FAST",
            [
                text_box(20, "Full ruleset\n約 99K rules", 0.9, 2.05, 2.5, 1.0, size=18, bold=True, fill="FFF7E6", line="E0C98F", align="ctr"),
                text_box(21, "selected bits\n12 個辨識 bit", 4.1, 2.05, 2.5, 1.0, size=18, bold=True, fill="EAF7FA", line="9CCBD8", align="ctr"),
                text_box(22, "bucket table\n4096 buckets", 7.3, 2.05, 2.5, 1.0, size=18, bold=True, fill="EDF7F1", line="9FC8AE", align="ctr"),
                text_box(23, "candidate bucket\n平均 169 rules", 10.2, 2.05, 2.35, 1.0, size=18, bold=True, fill="FFFFFF", line="A6B7C8", align="ctr"),
                text_box(24, "DBTable 的加速不是跳過規則判斷，而是避免每次都掃完整 ruleset。最後仍做 exact five-tuple match，所以可以維持分類正確性。", 1.0, 4.4, 11.0, 0.85, size=18, fill="FFFFFF", line="D6DEE7"),
            ],
            5,
        )
    )

    slides.append(
        slide(
            "代價：用建表成本與記憶體換查詢速度",
            "TRADEOFFS",
            [
                bullets(
                    [
                        "Build time：建表前要分析 ruleset，挑出 discriminative bits。",
                        "Memory：wildcard prefix 規則可能被放入多個 bucket，造成 replication。",
                        "Lookup：封包只進入相對小的候選 bucket，平均查詢成本下降。",
                        "適用情境：IP prefix 分布有可分辨性、查詢量很大、願意用建表換 lookup latency。",
                    ],
                    0.9,
                    2.0,
                    11.2,
                    3.4,
                    20,
                    size=17,
                )
            ],
            6,
        )
    )

    slides.append(
        slide(
            "架構流程：建表與查詢分成兩條路",
            "ARCHITECTURE",
            [
                text_box(20, "Rules", 0.8, 2.0, 1.4, 0.75, size=14, bold=True, fill="FFFFFF", line="A6B7C8", align="ctr"),
                text_box(21, "Parser", 2.7, 2.0, 1.4, 0.75, size=14, bold=True, fill="FFFFFF", line="A6B7C8", align="ctr"),
                text_box(22, "Bit ranking", 4.6, 2.0, 1.7, 0.75, size=14, bold=True, fill="FFFFFF", line="A6B7C8", align="ctr"),
                text_box(23, "Bucket table", 6.8, 2.0, 1.8, 0.75, size=14, bold=True, fill="FFFFFF", line="A6B7C8", align="ctr"),
                text_box(24, "Packet", 0.8, 4.0, 1.4, 0.75, size=14, bold=True, fill="FFF7E6", line="E0C98F", align="ctr"),
                text_box(25, "Key extraction", 2.7, 4.0, 1.8, 0.75, size=14, bold=True, fill="FFF7E6", line="E0C98F", align="ctr"),
                text_box(26, "Candidate bucket", 5.1, 4.0, 2.0, 0.75, size=14, bold=True, fill="FFF7E6", line="E0C98F", align="ctr"),
                text_box(27, "Exact match\n+ priority", 7.8, 4.0, 1.9, 0.75, size=14, bold=True, fill="FFF7E6", line="E0C98F", align="ctr"),
            ],
            7,
        )
    )

    slides.append(
        slide(
            "本專案實作：保留核心概念，讓實驗可重現",
            "IMPLEMENTATION",
            [
                table(
                    ["File", "Role"],
                    [
                        ["src/classbench.py", "解析 ClassBench rules/trace，做 exact five-tuple match。"],
                        ["src/dbtable_classifier.py", "選 discriminative bits，建立 bucket table，執行 lookup。"],
                        ["scripts/run_experiment.py", "量測 build time、lookup time、memory consumption。"],
                        ["scripts/validate_correctness.py", "用線性掃描 oracle 做抽樣正確性驗證。"],
                    ],
                    0.7,
                    1.9,
                    12.0,
                    0.62,
                    20,
                ),
                text_box(60, "限制：這是 DBTable-inspired 教學實作，不是 AMPS C++ DBTable 的完整逐行移植。", 0.95, 5.65, 11.2, 0.35, size=14, color="A23B3B", bold=True),
            ],
            8,
        )
    )

    slides.append(
        slide(
            "ClassBench ACL1 100K rules 作為測試資料集",
            "DATASET",
            [
                metric(20, f"{SUMMARY['rules_loaded']:,}", "valid parsed rules", 0.9, 2.05),
                metric(22, f"{SUMMARY['packets_tested']:,}", "packets tested", 3.55, 2.05),
                metric(24, f"{SUMMARY['bucket_count']:,}", "buckets", 6.2, 2.05),
                metric(26, f"{SUMMARY['average_bucket_size']:.1f}", "avg bucket size", 8.85, 2.05),
                bullets(
                    [
                        "資料位於 data/classbench/。",
                        "檔名為 100K，實際有效可解析規則數為 99,330。",
                        "外部參考實作保留於 external/amps，但不直接提交第三方 clone。",
                    ],
                    1.0,
                    4.1,
                    10.8,
                    1.4,
                    30,
                    size=16,
                ),
            ],
            9,
        )
    )

    slides.append(
        slide(
            "實驗結果：候選集合被縮小，lookup 只看小 bucket",
            "RESULTS",
            [
                metric(20, f"{SUMMARY['build_seconds']:.3f} s", "build time", 0.9, 2.05, "2E7D59"),
                metric(22, f"{SUMMARY['lookup_avg_ns']:.0f} ns", "average lookup", 3.55, 2.05, "2E7D59"),
                metric(24, f"{SUMMARY['lookup_p99_ns']:.0f} ns", "P99 lookup", 6.2, 2.05, "2E7D59"),
                metric(26, f"{SUMMARY['estimated_memory_bytes'] / 1048576:.2f} MiB", "estimated memory", 8.85, 2.05, "2E7D59"),
                bullets(
                    [
                        "4096 buckets 將近十萬規則分成平均約 169 筆的候選集合。",
                        "Lookup 成本主要由 candidate bucket scan 與 exact match 決定。",
                        "Correctness smoke test：200 sampled packets matched linear scan oracle。",
                    ],
                    1.0,
                    4.4,
                    10.8,
                    1.3,
                    30,
                    size=16,
                ),
            ],
            10,
        )
    )

    slides.append(
        slide(
            "與組員演算法比較時，用同一組核心指標",
            "COMPARISON",
            [
                table(
                    ["Dimension", "DBTable", "Group Algorithm A", "Group Algorithm B"],
                    [
                        ["Build", f"{SUMMARY['build_seconds']:.3f} s", "replace", "replace"],
                        ["Lookup", f"{SUMMARY['lookup_avg_ns']:.0f} ns avg", "replace", "replace"],
                        ["Memory", f"{SUMMARY['estimated_memory_bytes'] / 1048576:.2f} MiB", "replace", "replace"],
                        ["Best fit", "IP bits are discriminative", "replace", "replace"],
                    ],
                    0.65,
                    1.9,
                    12.0,
                    0.6,
                    20,
                ),
                text_box(60, "取得同組兩位同學的演算法與實測數據後，替換 Algorithm A/B 欄位即可。", 0.9, 5.8, 11.0, 0.3, size=14, color="52606D"),
            ],
            11,
        )
    )

    slides.append(
        slide(
            "結論：DBTable 的核心是先定位，再精確驗證",
            "CONCLUSION",
            [
                bullets(
                    [
                        "DBTable 不是用近似答案換速度，最後仍做完整五元組比對。",
                        "它把 ruleset 的分布特性轉換成 bucket index，減少平均 lookup 候選規則數。",
                        "優點是查詢快；代價是建表成本、記憶體與 wildcard replication。",
                        "本專案已完成資料集、程式、實驗、報告、PPT 與錄影講稿。",
                    ],
                    0.9,
                    2.0,
                    11.0,
                    3.2,
                    20,
                    size=17,
                )
            ],
            12,
        )
    )
    return slides


def write_package_parts(z: ZipFile, slide_count: int) -> None:
    overrides = [
        '<Override PartName="/ppt/presentation.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.presentation.main+xml"/>',
        '<Override PartName="/ppt/slideMasters/slideMaster1.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slideMaster+xml"/>',
        '<Override PartName="/ppt/slideLayouts/slideLayout1.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slideLayout+xml"/>',
        '<Override PartName="/ppt/theme/theme1.xml" ContentType="application/vnd.openxmlformats-officedocument.theme+xml"/>',
        '<Override PartName="/docProps/core.xml" ContentType="application/vnd.openxmlformats-package.core-properties+xml"/>',
        '<Override PartName="/docProps/app.xml" ContentType="application/vnd.openxmlformats-officedocument.extended-properties+xml"/>',
    ]
    overrides.extend(
        f'<Override PartName="/ppt/slides/slide{i}.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slide+xml"/>'
        for i in range(1, slide_count + 1)
    )
    z.writestr(
        "[Content_Types].xml",
        f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  {''.join(overrides)}
</Types>""",
    )
    z.writestr(
        "_rels/.rels",
        """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="ppt/presentation.xml"/>
  <Relationship Id="rId2" Type="http://schemas.openxmlformats.org/package/2006/relationships/metadata/core-properties" Target="docProps/core.xml"/>
  <Relationship Id="rId3" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/extended-properties" Target="docProps/app.xml"/>
</Relationships>""",
    )
    z.writestr(
        "docProps/core.xml",
        f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties" xmlns:dc="http://purl.org/dc/elements/1.1/"><dc:title>DBTable Packet Classification</dc:title><dc:creator>{esc(STUDENT)}</dc:creator><cp:lastModifiedBy>Codex</cp:lastModifiedBy></cp:coreProperties>""",
    )
    z.writestr(
        "docProps/app.xml",
        f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Properties xmlns="http://schemas.openxmlformats.org/officeDocument/2006/extended-properties" xmlns:vt="http://schemas.openxmlformats.org/officeDocument/2006/docPropsVTypes"><Application>Codex</Application><PresentationFormat>Wide</PresentationFormat><Slides>{slide_count}</Slides></Properties>""",
    )
    slide_ids = "".join(f'<p:sldId id="{255 + i}" r:id="rId{i + 1}"/>' for i in range(1, slide_count + 1))
    z.writestr(
        "ppt/presentation.xml",
        f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:presentation xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main">
  <p:sldMasterIdLst><p:sldMasterId id="2147483648" r:id="rId1"/></p:sldMasterIdLst>
  <p:sldIdLst>{slide_ids}</p:sldIdLst>
  <p:sldSz cx="{SLIDE_W}" cy="{SLIDE_H}" type="wide"/>
  <p:notesSz cx="6858000" cy="9144000"/>
</p:presentation>""",
    )
    rels = ['<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideMaster" Target="slideMasters/slideMaster1.xml"/>']
    rels.extend(
        f'<Relationship Id="rId{i + 1}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slide" Target="slides/slide{i}.xml"/>'
        for i in range(1, slide_count + 1)
    )
    z.writestr("ppt/_rels/presentation.xml.rels", f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">{''.join(rels)}</Relationships>""")
    z.writestr("ppt/slideMasters/slideMaster1.xml", f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?><p:sldMaster xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"><p:cSld><p:spTree><p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr><p:grpSpPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="{SLIDE_W}" cy="{SLIDE_H}"/><a:chOff x="0" y="0"/><a:chExt cx="{SLIDE_W}" cy="{SLIDE_H}"/></a:xfrm></p:grpSpPr></p:spTree></p:cSld><p:clrMap bg1="lt1" tx1="dk1" bg2="lt2" tx2="dk2" accent1="accent1" accent2="accent2" accent3="accent3" accent4="accent4" accent5="accent5" accent6="accent6" hlink="hlink" folHlink="folHlink"/><p:sldLayoutIdLst><p:sldLayoutId id="2147483649" r:id="rId1"/></p:sldLayoutIdLst><p:txStyles><p:titleStyle/><p:bodyStyle/><p:otherStyle/></p:txStyles></p:sldMaster>""")
    z.writestr("ppt/slideMasters/_rels/slideMaster1.xml.rels", """<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideLayout" Target="../slideLayouts/slideLayout1.xml"/><Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/theme" Target="../theme/theme1.xml"/></Relationships>""")
    z.writestr("ppt/slideLayouts/slideLayout1.xml", f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?><p:sldLayout xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main" type="blank"><p:cSld name="Blank"><p:spTree><p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr><p:grpSpPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="{SLIDE_W}" cy="{SLIDE_H}"/><a:chOff x="0" y="0"/><a:chExt cx="{SLIDE_W}" cy="{SLIDE_H}"/></a:xfrm></p:grpSpPr></p:spTree></p:cSld><p:clrMapOvr><a:masterClrMapping/></p:clrMapOvr></p:sldLayout>""")
    z.writestr("ppt/slideLayouts/_rels/slideLayout1.xml.rels", """<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideMaster" Target="../slideMasters/slideMaster1.xml"/></Relationships>""")
    z.writestr("ppt/theme/theme1.xml", """<?xml version="1.0" encoding="UTF-8" standalone="yes"?><a:theme xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" name="DBTable"><a:themeElements><a:clrScheme name="DBTable"><a:dk1><a:srgbClr val="14213D"/></a:dk1><a:lt1><a:srgbClr val="FFFFFF"/></a:lt1><a:dk2><a:srgbClr val="1F4E79"/></a:dk2><a:lt2><a:srgbClr val="F7FAFC"/></a:lt2><a:accent1><a:srgbClr val="2F9CBB"/></a:accent1><a:accent2><a:srgbClr val="2E7D59"/></a:accent2><a:accent3><a:srgbClr val="A23B3B"/></a:accent3><a:accent4><a:srgbClr val="52606D"/></a:accent4><a:accent5><a:srgbClr val="A6B7C8"/></a:accent5><a:accent6><a:srgbClr val="FFF7E6"/></a:accent6><a:hlink><a:srgbClr val="0563C1"/></a:hlink><a:folHlink><a:srgbClr val="954F72"/></a:folHlink></a:clrScheme><a:fontScheme name="Office"><a:majorFont><a:latin typeface="Microsoft JhengHei"/><a:ea typeface="Microsoft JhengHei"/></a:majorFont><a:minorFont><a:latin typeface="Microsoft JhengHei"/><a:ea typeface="Microsoft JhengHei"/></a:minorFont></a:fontScheme><a:fmtScheme name="Office"><a:fillStyleLst/><a:lnStyleLst/><a:effectStyleLst/><a:bgFillStyleLst/></a:fmtScheme></a:themeElements></a:theme>""")


def main() -> None:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    slides = build_slides()
    with ZipFile(OUT, "w", ZIP_DEFLATED) as z:
        write_package_parts(z, len(slides))
        for i, xml in enumerate(slides, start=1):
            z.writestr(f"ppt/slides/slide{i}.xml", xml)
            z.writestr(f"ppt/slides/_rels/slide{i}.xml.rels", """<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideLayout" Target="../slideLayouts/slideLayout1.xml"/></Relationships>""")
    print(json.dumps({"pptx": str(OUT), "slides": len(slides), "bytes": OUT.stat().st_size}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
