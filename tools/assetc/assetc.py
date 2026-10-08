#!/usr/bin/env python3
"""assetc - compile our own PNG art into the protocol 15.x asset format.

Input:  a manifest JSON describing every object/outfit/effect/missile and the
        PNG frames that make it up (paths relative to the manifest).
Output: <out>/appearances.dat, <out>/catalog-content.json and
        <out>/sprites-<first>-<last>.bmp.lzma sheets.

The same appearances.dat is read by the server (Canary) and the client
(OTClient), so both sides always agree on item ids and flags.

Manifest entry (all keys except id/frames optional):
{
  "id": 100, "name": "grass",
  "frames": ["floor/grass0.png"],          # 32x32 PNGs, one per sprite
  "size": [1, 1],                          # width/height in 32px tiles
  "patterns": [1, 1, 1], "layers": 1,      # x/y/z pattern dims (outfits: [4,1,1])
  "phases": 1, "phase_ms": 500,            # animation
  "flags": {"bank": 150, "unpass": true}   # AppearanceFlags fields
}
Outfits may give "idle" and "moving" frame lists instead of "frames".
"""
import argparse
import json
import lzma
import struct
import sys
from pathlib import Path

from PIL import Image

sys.path.insert(0, str(Path(__file__).parent))
import appearances_pb2 as pb  # noqa: E402

SHEET = 384
TILE = 32
# sprite layout index -> (w, h), must match OTClient SpriteSheet::getSpriteSize
LAYOUTS = {(32, 32): 0, (32, 64): 1, (64, 32): 2, (64, 64): 3}
CIP_MAGIC = bytes([0x70, 0x0A, 0xFA, 0x80, 0x24])
LZMA_FILTER = {"id": lzma.FILTER_LZMA1, "dict_size": 1 << 25, "lc": 3, "lp": 0, "pb": 2}


# ---------------------------------------------------------------- sprites
class SheetPacker:
    """Packs equal-size sprites into 384x384 sheets, one layout per sheet."""

    def __init__(self):
        self.next_id = 1
        self.open = {}      # layout -> current sheet dict
        self.sheets = []    # finished + open sheets in id order

    def add(self, img: Image.Image) -> int:
        w, h = img.size
        layout = LAYOUTS[(w, h)]
        sheet = self.open.get(layout)
        per_sheet = (SHEET // w) * (SHEET // h)
        if sheet is None or len(sheet["sprites"]) == per_sheet or sheet["last"] != self.next_id - 1:
            sheet = {"layout": layout, "size": (w, h), "first": self.next_id,
                     "last": self.next_id - 1, "sprites": []}
            self.open[layout] = sheet
            self.sheets.append(sheet)
        sid = self.next_id
        sheet["sprites"].append(img)
        sheet["last"] = sid
        self.next_id += 1
        return sid


def encode_7bit(n: int) -> bytes:
    out = bytearray()
    while True:
        b = n & 0x7F
        n >>= 7
        if n:
            out.append(b | 0x80)
        else:
            out.append(b)
            return bytes(out)


def sheet_to_bmp(sheet) -> bytes:
    w, h = sheet["size"]
    canvas = Image.new("RGBA", (SHEET, SHEET), (0, 0, 0, 0))
    cols = SHEET // w
    for i, img in enumerate(sheet["sprites"]):
        canvas.paste(img, ((i % cols) * w, (i // cols) * h))
    # 32bpp BGRA, bottom-up rows (the client swaps B/R and flips vertically)
    r, g, b, a = canvas.split()
    raw = Image.merge("RGBA", (b, g, r, a)).transpose(Image.FLIP_TOP_BOTTOM).tobytes()
    header_size = 14 + 40
    file_header = b"BM" + struct.pack("<IHHI", header_size + len(raw), 0, 0, header_size)
    info = struct.pack("<IiiHHIIiiII", 40, SHEET, SHEET, 1, 32, 0, len(raw), 2835, 2835, 0, 0)
    return file_header + info + raw


def compress_cip(bmp: bytes) -> bytes:
    body = lzma.compress(bmp, format=lzma.FORMAT_RAW, filters=[LZMA_FILTER])
    f = LZMA_FILTER
    props = bytes([(f["pb"] * 5 + f["lp"]) * 9 + f["lc"]]) + struct.pack("<I", f["dict_size"])
    payload = props + struct.pack("<Q", len(bmp)) + body
    size = encode_7bit(len(payload))
    header = b"\x00" * (32 - len(CIP_MAGIC) - len(size)) + CIP_MAGIC + size
    assert len(header) == 32
    return header + payload


# ---------------------------------------------------------------- appearances
def load_png(base: Path, rel: str, size):
    img = Image.open(base / rel).convert("RGBA")
    want = (size[0] * TILE, size[1] * TILE)
    if img.size != want:
        img = img.resize(want, Image.NEAREST)
    return img


def set_flags(msg, flags: dict):
    for key, val in flags.items():
        field = msg.DESCRIPTOR.fields_by_name[key]
        if field.message_type is None:
            setattr(msg, key, val)
            continue
        sub = getattr(msg, key)
        if isinstance(val, dict):
            for k, v in val.items():
                setattr(sub, k, v)
        else:  # shorthand: first field of the sub-message
            setattr(sub, field.message_type.fields[0].name, val)


def frame_group(packer, base, entry, frames, group):
    size = entry.get("size", [1, 1])
    pw, ph, pd = entry.get("patterns", [1, 1, 1])
    layers = entry.get("layers", 1)
    phases = entry.get("phases", 1)
    expected = pw * ph * pd * layers * phases
    if len(frames) != expected:
        raise SystemExit(f"id {entry['id']}: {len(frames)} frames, expected {expected}")
    fg = pb.FrameGroup(fixed_frame_group=group, id=0)
    info = fg.sprite_info
    info.pattern_width, info.pattern_height, info.pattern_depth = pw, ph, pd
    info.layers = layers
    info.bounding_square = max(size) * TILE
    for rel in frames:
        info.sprite_id.append(packer.add(load_png(base, rel, size)))
    if phases > 1:
        anim = info.animation
        anim.default_start_phase = 0
        anim.synchronized = entry.get("synchronized", True)
        anim.loop_type = pb.ANIMATION_LOOP_TYPE_INFINITE
        ms = entry.get("phase_ms", 500)
        for _ in range(phases):
            anim.sprite_phase.add(duration_min=ms, duration_max=ms)
    return fg


def build(manifest_path: Path, out: Path):
    base = manifest_path.parent
    manifest = json.loads(manifest_path.read_text())
    packer = SheetPacker()
    apps = pb.Appearances()
    categories = [("objects", apps.object), ("outfits", apps.outfit),
                  ("effects", apps.effect), ("missiles", apps.missile)]
    for key, target in categories:
        seen = set()
        for entry in sorted(manifest.get(key, []), key=lambda e: e["id"]):
            if entry["id"] in seen:
                raise SystemExit(f"duplicate {key} id {entry['id']}")
            seen.add(entry["id"])
            app = target.add(id=entry["id"])
            if entry.get("name"):
                app.name = entry["name"]
            if key == "outfits":
                app.frame_group.append(frame_group(packer, base, entry, entry["idle"],
                                                   pb.FIXED_FRAME_GROUP_OUTFIT_IDLE))
                moving = dict(entry, phases=entry.get("moving_phases", entry.get("phases", 1)))
                app.frame_group.append(frame_group(packer, base, moving, entry["moving"],
                                                   pb.FIXED_FRAME_GROUP_OUTFIT_MOVING))
            else:
                app.frame_group.append(frame_group(packer, base, entry, entry["frames"],
                                                   pb.FIXED_FRAME_GROUP_OBJECT_INITIAL))
            set_flags(app.flags, entry.get("flags", {}))
    special = manifest.get("special", {})
    if special:
        set_flags(apps.special_meaning_appearance_ids, special)

    out.mkdir(parents=True, exist_ok=True)
    for old in out.glob("sprites-*.bmp.lzma"):
        old.unlink()
    (out / "appearances.dat").write_bytes(apps.SerializeToString())
    # empty staticdata (bestiary/boss metadata) - the client requires the file to exist
    (out / "staticdata.dat").write_bytes(b"")
    catalog = [{"type": "appearances", "file": "appearances.dat"},
               {"type": "staticdata", "file": "staticdata.dat"}]
    for sheet in packer.sheets:
        name = f"sprites-{sheet['first']}-{sheet['last']}.bmp.lzma"
        (out / name).write_bytes(compress_cip(sheet_to_bmp(sheet)))
        catalog.append({"type": "sprite", "file": name, "spritetype": sheet["layout"],
                        "firstspriteid": sheet["first"], "lastspriteid": sheet["last"],
                        "area": 0})
    (out / "catalog-content.json").write_text(json.dumps(catalog, indent=1))
    print(f"{sum(len(t) for _, t in categories)} appearances, "
          f"{packer.next_id - 1} sprites, {len(packer.sheets)} sheets -> {out}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("manifest", type=Path)
    ap.add_argument("out", type=Path)
    a = ap.parse_args()
    build(a.manifest, a.out)
