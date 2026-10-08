#!/usr/bin/env python3
"""Generate the server's items.xml from assets/manifest.json.

Usage: items_xml.py <manifest.json> <out items.xml>
"""
import json
import sys
from pathlib import Path
from xml.sax.saxutils import quoteattr

manifest = json.loads(Path(sys.argv[1]).read_text())
lines = ['<?xml version="1.0" encoding="UTF-8"?>', "<items>"]
for o in sorted(manifest["objects"], key=lambda e: e["id"]):
    srv = o.get("server", {})
    head = f'\t<item id="{o["id"]}"'
    if srv.get("article"):
        head += f' article={quoteattr(srv["article"])}'
    head += f' name={quoteattr(o.get("name", ""))}'
    attrs = srv.get("attrs", {})
    script = srv.get("script")
    if not attrs and not script:
        lines.append(head + "/>")
        continue
    lines.append(head + ">")
    for k, v in attrs.items():
        lines.append(f'\t\t<attribute key="{k}" value="{v}"/>')
    if script:
        kind, sub = script
        lines.append(f'\t\t<attribute key="script" value="{kind}">')
        for k, v in sub.items():
            lines.append(f'\t\t\t<attribute key="{k}" value="{v}"/>')
        lines.append("\t\t</attribute>")
    lines.append("\t</item>")
lines.append("</items>")
Path(sys.argv[2]).write_text("\n".join(lines) + "\n")
print(f"items.xml: {len(manifest['objects'])} items")
