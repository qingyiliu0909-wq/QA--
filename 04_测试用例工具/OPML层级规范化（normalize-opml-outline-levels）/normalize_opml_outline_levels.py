# -*- coding: utf-8 -*-
"""
Normalize OPML outline structure so that within each TC node:
  前置条件 / 测试步骤 / 预期结果
are siblings (same level), not nested inside each other.
"""

from __future__ import annotations

from pathlib import Path
import xml.etree.ElementTree as ET


PRE = "前置条件"
STEP = "测试步骤"
EXP = "预期结果"


def text(el: ET.Element) -> str | None:
    return el.attrib.get("text")


def detach_first(parent: ET.Element, label: str) -> ET.Element | None:
    for ch in list(parent):
        if ch.tag == "outline" and text(ch) == label:
            parent.remove(ch)
            return ch
    return None


def normalize_tc(tc: ET.Element) -> None:
    pre = None
    for ch in list(tc):
        if ch.tag == "outline" and text(ch) == PRE:
            pre = ch
            break
    if pre is None:
        return

    step = None
    exp = None

    # 1) If STEP is incorrectly nested under PRE, detach it.
    step = detach_first(pre, STEP)

    # 2) If EXP is incorrectly nested under STEP (nested under PRE), detach it and keep it.
    if step is not None:
        exp = detach_first(step, EXP)
    else:
        exp = None

    # 3) If EXP is incorrectly nested under PRE (rare), detach it.
    if exp is None:
        exp = detach_first(pre, EXP)

    # 4) If EXP exists but is still nested under STEP (other formatting variants), pull it out.
    if step is not None and exp is None:
        exp = detach_first(step, EXP)

    # Insert STEP/EXP as siblings in correct order.
    kids = list(tc)
    pre_idx = kids.index(pre)
    insert_idx = pre_idx + 1

    if step is not None:
        tc.insert(insert_idx, step)
        insert_idx += 1
    if exp is not None:
        tc.insert(insert_idx, exp)


def walk(el: ET.Element) -> None:
    t = text(el)
    if el.tag == "outline" and isinstance(t, str) and t.startswith("TC-"):
        normalize_tc(el)
    for ch in list(el):
        # Recurse through the full XML tree (opml/head/body/outline...)
        walk(ch)


def main() -> None:
    opml_path = Path(r"d:\OBT_1.4_Internal\config_analysis\护送玩法_测试用例.opml")
    raw = opml_path.read_bytes()
    # Some OPML exports are saved as GBK/ANSI while claiming UTF-8.
    # Decode robustly so we can reliably match Chinese node titles.
    decoded = None
    for enc in ("utf-8", "gbk"):
        try:
            s = raw.decode(enc)
        except UnicodeDecodeError:
            continue
        if PRE in s and STEP in s and EXP in s:
            decoded = s
            break
        # If it doesn't contain the expected Chinese strings, still keep as fallback.
        decoded = s
    if decoded is None:
        raise RuntimeError("Unable to decode OPML file as utf-8 or gbk.")

    root = ET.fromstring(decoded)
    walk(root)
    opml_path.write_bytes(ET.tostring(root, encoding="utf-8", xml_declaration=True))


if __name__ == "__main__":
    main()

