#!/usr/bin/env python3
"""Decode compiled assets exactly the way OTClient does, and dump a preview.

Usage: verify.py <asset dir> [preview.png]
"""
import json
import lzma
import struct
import sys
from pathlib import Path

from PIL import Image

sys.path.insert(0, str(Path(__file__).parent))
import appearances_pb2 as pb  # noqa: E402

SIZES = {0: (32, 32), 1: (32, 64), 2: (64, 32), 3: (64, 64)}


def decode_sheet(data: bytes) -> Image.Image:
    i = 0
    while data[i] == 0:                     # while (fin->getU8() == 0x00);
        i += 1
    i += 1 + 4                              # that read byte was the first magic byte; skip(4)
    while data[i] & 0x80:                   # 7-bit size
        i += 1
    i += 1
    lclppb = data[i]; i += 1
    lc, rem = lclppb % 9, lclppb // 9
    lp, pbits = rem % 5, rem // 5
    dict_size = struct.unpack_from("<I", data, i)[0]; i += 4
    i += 8                                  # cip compressed size
    dec = lzma.LZMADecompressor(lzma.FORMAT_RAW, filters=[
        {"id": lzma.FILTER_LZMA1, "dict_size": dict_size, "lc": lc, "lp": lp, "pb": pbits}])
    bmp = dec.decompress(data[i:])
    assert dec.eof, "no LZMA end marker: client would reject (needs LZMA_STREAM_END)"
    assert len(bmp) <= 384 * 384 * 4 + 122, "sheet larger than client buffer"
    off = struct.unpack_from("<I", bmp, 10)[0]
    raw = bmp[off:off + 384 * 384 * 4]
    b, g, r, a = Image.frombytes("RGBA", (384, 384), raw).split()
    return Image.merge("RGBA", (r, g, b, a)).transpose(Image.FLIP_TOP_BOTTOM)


def main():
    root = Path(sys.argv[1])
    catalog = json.loads((root / "catalog-content.json").read_text())
    apps = pb.Appearances()
    apps.ParseFromString((root / "appearances.dat").read_bytes())
    sheets = []
    for e in catalog:
        if e["type"] == "sprite":
            sheets.append((e, decode_sheet((root / e["file"]).read_bytes())))

    def sprite(sid):
        for e, img in sheets:
            if e["firstspriteid"] <= sid <= e["lastspriteid"]:
                w, h = SIZES[e["spritetype"]]
                cols = 384 // w
                k = sid - e["firstspriteid"]
                return img.crop(((k % cols) * w, (k // cols) * h, (k % cols) * w + w, (k // cols) * h + h))
        raise SystemExit(f"sprite {sid} not in any sheet")

    things = list(apps.object) + list(apps.outfit)
    print(f"objects={len(apps.object)} outfits={len(apps.outfit)} effects={len(apps.effect)} "
          f"missiles={len(apps.missile)} sheets={len(sheets)}")
    if len(sys.argv) > 2:
        cols = 16
        prev = Image.new("RGBA", (cols * 64, ((len(things) + cols - 1) // cols) * 64), (40, 40, 40, 255))
        for n, t in enumerate(things):
            s = sprite(t.frame_group[0].sprite_info.sprite_id[0])
            prev.alpha_composite(s, ((n % cols) * 64 + (64 - s.width) // 2, (n // cols) * 64 + (64 - s.height) // 2))
        prev.save(sys.argv[2])
        print("preview ->", sys.argv[2])
    else:
        for t in things:
            for fg in t.frame_group:
                for sid in fg.sprite_info.sprite_id:
                    sprite(sid)
    print("OK")


if __name__ == "__main__":
    main()
