#!/usr/bin/env python3
"""Generate the starter world: the town of Hunter's Rest and its hunting grounds.

Usage: world.py <out dir>   -> hunterrealms.otbm + spawn/npc/house/zone XML
Deterministic (seeded) so regenerating gives the same map.
"""
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from otbm import (FLAG_PZ, Map, ATTR_SPAWN_MONSTER_FILE, ATTR_SPAWN_NPC_FILE,  # noqa: E402
                  ATTR_HOUSE_FILE, ATTR_ZONE_FILE)

# item ids (see assets/manifest.json)
GRASS, GRASS2, DIRT, COBBLE, SAND, WOODFLOOR = 60100, 60101, 60102, 60103, 60104, 60105
SHALLOW, DEEP = 60110, 60111
WALLS = [60200, 60201, 60202, 60203]
BRICK = 60210
TREES = [60300, 60301]
DOOR = 60400

Z = 7
CX, CY = 1000, 1000          # town centre
R = 70                        # island radius
rng = random.Random(1337)
m = Map(2048, 2048, "Hunter Realms - starter island")
m.files = {ATTR_SPAWN_MONSTER_FILE: "hunterrealms-monster.xml",
           ATTR_SPAWN_NPC_FILE: "hunterrealms-npc.xml",
           ATTR_HOUSE_FILE: "hunterrealms-house.xml",
           ATTR_ZONE_FILE: "hunterrealms-zones.xml"}

blocked = set()   # tiles with walls/trees/water so spawns avoid them
reserved = set()  # town & paths: no trees


def ground(x, y, item):
    m.set_ground(x, y, Z, item)


def block(x, y, item):
    m.add_item(x, y, Z, item)
    blocked.add((x, y))


# 1. island: grass inside radius, sand shore, shallow then deep water
for y in range(CY - R - 6, CY + R + 7):
    for x in range(CX - R - 6, CX + R + 7):
        d = ((x - CX) ** 2 + (y - CY) ** 2) ** 0.5 + rng.uniform(-2.5, 2.5)
        if d < R - 3:
            ground(x, y, rng.choice([GRASS, GRASS, GRASS2]))
        elif d < R:
            ground(x, y, SAND)
        elif d < R + 2:
            ground(x, y, SHALLOW)
        else:
            ground(x, y, DEEP)
            blocked.add((x, y))

# 2. town plaza (cobblestone), with dirt roads out to the four hunting grounds
for y in range(CY - 12, CY + 13):
    for x in range(CX - 12, CX + 13):
        ground(x, y, COBBLE)
        reserved.add((x, y))
for i in range(13, R - 4):
    for w in (-1, 0, 1):
        for x, y in ((CX + w, CY - i), (CX + w, CY + i), (CX + i, CY + w), (CX - i, CY + w)):
            ground(x, y, DIRT)
            reserved.add((x, y))

# 3. temple: walled 9x9 building north of plaza centre, protection zone inside
TX0, TY0, TX1, TY1 = CX - 4, CY - 11, CX + 4, CY - 3
for y in range(TY0, TY1 + 1):
    for x in range(TX0, TX1 + 1):
        edge = x in (TX0, TX1) or y in (TY0, TY1)
        ground(x, y, WOODFLOOR)
        m.tile(x, y, Z)["flags"] = FLAG_PZ
        if edge and not (y == TY1 and x == CX):
            block(x, y, WALLS[(x + y) % 4])
TEMPLE = (CX, CY - 7, Z)

# 4. shop: small brick building east of plaza
SX0, SY0, SX1, SY1 = CX + 5, CY - 2, CX + 11, CY + 4
for y in range(SY0, SY1 + 1):
    for x in range(SX0, SX1 + 1):
        ground(x, y, WOODFLOOR)
        m.tile(x, y, Z)["flags"] = FLAG_PZ
        if (x in (SX0, SX1) or y in (SY0, SY1)) and not (x == SX0 and y == CY + 1):
            block(x, y, BRICK)
SHOPKEEPER = (CX + 8, CY + 1, Z)

# 5. trees: scattered, denser further from town, never on roads/town
for y in range(CY - R, CY + R):
    for x in range(CX - R, CX + R):
        if (x, y) in reserved or (x, y) in blocked:
            continue
        d = ((x - CX) ** 2 + (y - CY) ** 2) ** 0.5
        if 18 < d < R - 4 and rng.random() < 0.04 + 0.06 * (d / R):
            block(x, y, rng.choice(TREES))

# 6. a stream crossing the east road (walkable shallow water)
for y in range(CY - R, CY + R):
    x = CX + 35 + int(4 * __import__("math").sin(y / 6))
    for w in (0, 1, 2):
        if (x + w, y, Z) in m.tiles and (x + w, y) not in blocked and \
                ((x + w - CX) ** 2 + (y - CY) ** 2) ** 0.5 < R - 3:
            m.set_ground(x + w, y, Z, SHALLOW)

m.towns = [(1, "Hunter's Rest", TEMPLE)]
m.waypoints = [("temple", TEMPLE)]

# 7. hunting grounds: (name, centre, monster names, count, level hint)
grounds = [
    ("north fields", (CX, CY - 40), ["Rat"], 14),
    ("west woods", (CX - 40, CY), ["Jackal", "Bat"], 12),
    ("east hills", (CX + 48, CY), ["Goblin"], 12),
    ("south camp", (CX, CY + 45), ["Orc", "Goblin"], 12),
]
spawns = []
land = {(k[0], k[1]) for k in m.tiles}
for name, (gx, gy), kinds, count in grounds:
    placed = 0
    while placed < count:
        x, y = gx + rng.randint(-12, 12), gy + rng.randint(-12, 12)
        if (x, y) in blocked or (x, y) in reserved or (x, y) not in land:
            continue
        spawns.append((x, y, rng.choice(kinds)))
        blocked.add((x, y))
        placed += 1

out = Path(sys.argv[1])
out.mkdir(parents=True, exist_ok=True)
m.write(out / "hunterrealms.otbm")

lines = ['<?xml version="1.0"?>', "<monsters>"]
for x, y, kind in spawns:
    lines += [f'\t<monster centerx="{x}" centery="{y}" centerz="{Z}" radius="3">',
              f'\t\t<monster name="{kind}" x="0" y="0" z="{Z}" spawntime="60" />',
              "\t</monster>"]
lines.append("</monsters>")
(out / "hunterrealms-monster.xml").write_text("\n".join(lines) + "\n")

sx, sy, sz = SHOPKEEPER
(out / "hunterrealms-npc.xml").write_text(
    '<?xml version="1.0"?>\n<npcs>\n'
    f'\t<npc centerx="{sx}" centery="{sy}" centerz="{sz}" radius="1">\n'
    f'\t\t<npc name="Mara" x="0" y="0" z="{sz}" spawntime="60" />\n'
    "\t</npc>\n</npcs>\n")
(out / "hunterrealms-house.xml").write_text('<?xml version="1.0"?>\n<houses />\n')
(out / "hunterrealms-zones.xml").write_text('<?xml version="1.0"?>\n<zones />\n')
print(f"{len(m.tiles)} tiles, {len(spawns)} monsters, temple at {TEMPLE}")
