#!/usr/bin/env python3
"""Parse an .otbm the way the server does and render a top-down preview.

Usage: preview.py <map.otbm> <manifest.json> <monster.xml> <out.png> [px per tile]
"""
import json
import struct
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

from PIL import Image, ImageDraw

ESC, START, END = 0xFD, 0xFE, 0xFF


def parse(data):
    """Return nested nodes: (type, payload bytes, children)."""
    pos = 4

    def node():
        nonlocal pos
        assert data[pos] == START, f"expected node start at {pos}"
        pos += 1
        payload = bytearray()
        children = []
        while True:
            b = data[pos]
            if b == ESC:
                payload.append(data[pos + 1]); pos += 2
            elif b == START:
                children.append(node())
            elif b == END:
                pos += 1
                return payload[0], bytes(payload[1:]), children
            else:
                payload.append(b); pos += 1
    root = node()
    assert pos == len(data), "trailing bytes after root"
    return root


def tiles(root):
    _, hdr, kids = root
    version, w, h, major, minor = struct.unpack_from("<IHHII", hdr)
    md = kids[0]
    out, towns = {}, []
    for t, p, ch in md[2]:
        if t == 4:  # tile area
            bx, by, bz = struct.unpack_from("<HHB", p)
            for tt, tp, tch in ch:
                x, y = bx + tp[0], by + tp[1]
                items, i = [], 2
                while i < len(tp):
                    a = tp[i]; i += 1
                    if a == 3: i += 4
                    elif a == 9: items.append(struct.unpack_from("<H", tp, i)[0]); i += 2
                    else: raise SystemExit(f"unknown tile attr {a}")
                items += [struct.unpack_from("<H", ip)[0] for _, ip, _ in tch]
                out[(x, y, bz)] = items
        elif t == 12:
            for _, tp, _ in ch:
                tid, ln = struct.unpack_from("<IH", tp)
                name = tp[6:6 + ln].decode()
                x, y, z = struct.unpack_from("<HHB", tp, 6 + ln)
                towns.append((tid, name, (x, y, z)))
    return out, towns


def main():
    mp, man, mon, outp = sys.argv[1:5]
    px = int(sys.argv[5]) if len(sys.argv) > 5 else 8
    root = parse(Path(mp).read_bytes())
    tl, towns = tiles(root)
    manifest = json.loads(Path(man).read_text())
    base = Path(man).parent
    sprite = {}
    for e in manifest["objects"]:
        sprite[e["id"]] = Image.open(base / e["frames"][0]).convert("RGBA").resize((px, px), Image.NEAREST)
    xs = [k[0] for k in tl]; ys = [k[1] for k in tl]
    x0, y0 = min(xs), min(ys)
    img = Image.new("RGBA", ((max(xs) - x0 + 1) * px, (max(ys) - y0 + 1) * px), (0, 0, 0, 255))
    for (x, y, z), items in tl.items():
        for it in items:
            img.alpha_composite(sprite[it], ((x - x0) * px, (y - y0) * px))
    d = ImageDraw.Draw(img)
    for m in ET.parse(mon).getroot():
        x, y = int(m.get("centerx")), int(m.get("centery"))
        d.ellipse([(x - x0) * px + 1, (y - y0) * px + 1, (x - x0 + 1) * px - 1, (y - y0 + 1) * px - 1], fill=(220, 30, 30, 255))
    for _, name, (x, y, z) in towns:
        d.rectangle([(x - x0) * px, (y - y0) * px, (x - x0 + 1) * px, (y - y0 + 1) * px], outline=(255, 255, 0, 255), width=2)
    img.save(outp)
    print(f"{len(tl)} tiles parsed, towns={towns}, preview -> {outp}")


if __name__ == "__main__":
    main()
