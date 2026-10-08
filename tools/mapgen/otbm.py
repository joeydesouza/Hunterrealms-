"""Minimal OTBM (map) writer compatible with Canary's IOMap loader."""
import struct

NODE_ESC, NODE_START, NODE_END = 0xFD, 0xFE, 0xFF

OTBM_ROOT, OTBM_MAP_DATA, OTBM_TILE_AREA, OTBM_TILE, OTBM_ITEM = 0, 2, 4, 5, 6
OTBM_TOWNS, OTBM_TOWN, OTBM_WAYPOINTS, OTBM_WAYPOINT = 12, 13, 15, 16
ATTR_DESCRIPTION, ATTR_TILE_FLAGS, ATTR_ITEM = 1, 3, 9
ATTR_ACTION_ID, ATTR_UNIQUE_ID, ATTR_TELE_DEST, ATTR_COUNT = 4, 5, 8, 15
ATTR_SPAWN_MONSTER_FILE, ATTR_HOUSE_FILE, ATTR_SPAWN_NPC_FILE, ATTR_ZONE_FILE = 11, 13, 23, 24

FLAG_PZ, FLAG_NOPVP, FLAG_NOLOGOUT, FLAG_PVP = 1, 4, 8, 16


class Node:
    def __init__(self, type_, data=b""):
        self.type, self.data, self.children = type_, bytearray(data), []

    def add(self, child):
        self.children.append(child)
        return child

    def serialize(self, out: bytearray):
        out.append(NODE_START)
        for b in bytes([self.type]) + bytes(self.data):
            if b in (NODE_ESC, NODE_START, NODE_END):
                out.append(NODE_ESC)
            out.append(b)
        for c in self.children:
            c.serialize(out)
        out.append(NODE_END)


def u8(v): return struct.pack("<B", v)
def u16(v): return struct.pack("<H", v)
def u32(v): return struct.pack("<I", v)
def string(s): b = s.encode(); return u16(len(b)) + b


class Map:
    def __init__(self, width, height, description=""):
        self.width, self.height, self.description = width, height, description
        self.tiles = {}       # (x,y,z) -> {"items": [ids...], "flags": int}
        self.towns = []       # (id, name, (x,y,z))
        self.waypoints = []   # (name, (x,y,z))
        self.files = {}       # attr -> filename

    def tile(self, x, y, z):
        return self.tiles.setdefault((x, y, z), {"items": [], "flags": 0, "attrs": {}})

    def set_ground(self, x, y, z, item_id):
        t = self.tile(x, y, z)
        t["items"] = [item_id] + t["items"][1:] if t["items"] else [item_id]

    def add_item(self, x, y, z, item_id, **attrs):
        t = self.tile(x, y, z)
        t["items"].append(item_id)
        if attrs:
            t["attrs"][len(t["items"]) - 1] = attrs

    def write(self, path):
        root = Node(OTBM_ROOT, u32(2) + u16(self.width) + u16(self.height) + u32(3) + u32(57))
        md = Node(OTBM_MAP_DATA)
        md.data += u8(ATTR_DESCRIPTION) + string(self.description)
        for attr, name in self.files.items():
            md.data += u8(attr) + string(name)
        root.add(md)
        areas = {}
        for (x, y, z), t in sorted(self.tiles.items()):
            if not t["items"]:
                continue
            key = (x & 0xFF00, y & 0xFF00, z)
            area = areas.get(key)
            if area is None:
                area = areas[key] = md.add(Node(OTBM_TILE_AREA, u16(key[0]) + u16(key[1]) + u8(z)))
            tile = area.add(Node(OTBM_TILE, u8(x & 0xFF) + u8(y & 0xFF)))
            if t["flags"]:
                tile.data += u8(ATTR_TILE_FLAGS) + u32(t["flags"])
            for idx, item_id in enumerate(t["items"]):
                attrs = t["attrs"].get(idx)
                if idx == 0 and not attrs:
                    tile.data += u8(ATTR_ITEM) + u16(item_id)   # ground shorthand
                    continue
                node = tile.add(Node(OTBM_ITEM, u16(item_id)))
                for k, v in (attrs or {}).items():
                    if k == "aid":
                        node.data += u8(ATTR_ACTION_ID) + u16(v)
                    elif k == "uid":
                        node.data += u8(ATTR_UNIQUE_ID) + u16(v)
                    elif k == "count":
                        node.data += u8(ATTR_COUNT) + u8(v)
                    elif k == "dest":
                        node.data += u8(ATTR_TELE_DEST) + u16(v[0]) + u16(v[1]) + u8(v[2])
        towns = md.add(Node(OTBM_TOWNS))
        for tid, name, (x, y, z) in self.towns:
            towns.add(Node(OTBM_TOWN, u32(tid) + string(name) + u16(x) + u16(y) + u8(z)))
        wps = md.add(Node(OTBM_WAYPOINTS))
        for name, (x, y, z) in self.waypoints:
            wps.add(Node(OTBM_WAYPOINT, string(name) + u16(x) + u16(y) + u8(z)))
        out = bytearray(b"\x00\x00\x00\x00")   # file identifier
        root.serialize(out)
        with open(path, "wb") as f:
            f.write(out)
