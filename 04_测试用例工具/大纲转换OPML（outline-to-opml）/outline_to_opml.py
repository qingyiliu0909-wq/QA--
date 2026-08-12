import html
from pathlib import Path


def parse_tab_indented(lines: list[str]) -> dict:
    """
    Parse tab-indented outline into a tree.
    Each line is a node. Leading tabs indicate depth.
    Returns root node: {"text": "...", "children": [...]}
    """
    root = {"text": "ROOT", "children": []}
    stack = [( -1, root)]  # (depth, node)

    for raw in lines:
        line = raw.rstrip("\r\n")
        if not line.strip():
            continue

        # Count leading tabs; also treat leading 4-space groups as tabs.
        depth = 0
        i = 0
        while i < len(line):
            if line[i] == "\t":
                depth += 1
                i += 1
            elif line.startswith("    ", i):
                depth += 1
                i += 4
            else:
                break

        text = line[i:].strip()
        node = {"text": text, "children": []}

        # Pop to parent depth
        while stack and stack[-1][0] >= depth:
            stack.pop()
        parent = stack[-1][1] if stack else root
        parent["children"].append(node)
        stack.append((depth, node))

    return root


def node_to_opml_outline(node: dict, indent: str = "      ") -> str:
    # node: {"text":..., "children":[...]}
    # Escape for XML attribute.
    txt = html.escape(node["text"], quote=True)
    if not node["children"]:
        return f'{indent}<outline text="{txt}" />\n'
    s = f'{indent}<outline text="{txt}">\n'
    for child in node["children"]:
        s += node_to_opml_outline(child, indent + "  ")
    s += f"{indent}</outline>\n"
    return s


def main() -> None:
    src = Path(r"d:\OBT_1.4_Internal\config_analysis\护送玩法_测试用例.fixed.xmind_import.txt")
    dst = Path(r"d:\OBT_1.4_Internal\config_analysis\护送玩法_测试用例.opml")

    lines = src.read_text(encoding="utf-8").splitlines()
    tree = parse_tab_indented(lines)

    # Use the first non-empty top-level node as title if present.
    title = "Outline"
    for c in tree["children"]:
        if c["text"]:
            title = c["text"]
            break

    body = ""
    for child in tree["children"]:
        body += node_to_opml_outline(child)

    opml = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<opml version="2.0">\n'
        "  <head>\n"
        f"    <title>{html.escape(title)}</title>\n"
        "  </head>\n"
        "  <body>\n"
        f"{body}"
        "  </body>\n"
        "</opml>\n"
    )
    dst.write_text(opml, encoding="utf-8")
    print(f"Wrote: {dst}")


if __name__ == "__main__":
    main()

