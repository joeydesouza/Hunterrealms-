#!/usr/bin/env python3
"""Copy the starter CC0 tiles into assets/art and write assets/manifest.json.

Item id ranges (ours, not Tibia's):
  100-199 grounds   200-299 walls/borders   300-399 nature/decor
  400-499 doors     1000+  items            outfits 1+   monsters 100+
"""
import json
import shutil
import sys
from pathlib import Path

SRC = Path(sys.argv[1])            # crawl-tiles/releases/Nov-2015
ROOT = Path(sys.argv[2])           # game repo root
ART = ROOT / "assets" / "art"

objects, outfits = [], []


def art(rel):
    dst = ART / rel
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy(SRC / rel, dst)
    return f"art/{rel}"


def obj(id_, name, rel, **flags):
    objects.append({"id": id_, "name": name, "frames": [art(rel)], "flags": flags})


# grounds: bank = walking speed (lower is faster, Tibia-style 100-200)
obj(100, "grass", "dngn/floor/grass/grass0.png", bank=150, automap=0x18)
obj(101, "grass", "dngn/floor/grass/grass1.png", bank=150, automap=0x18)
obj(102, "dirt", "dngn/floor/dirt0.png", bank=160, automap=0x79)
obj(103, "cobblestone", "dngn/floor/pebble_brown0.png", bank=120, automap=0x56)
obj(104, "sand", "dngn/floor/sand1.png", bank=170, automap=0xCF)
obj(105, "wooden floor", "dngn/floor/limestone0.png", bank=120, automap=0x79)
objects.append({"id": 110, "name": "shallow water", "frames":
                [art("dngn/water/shallow_water.png"), art("dngn/water/shallow_water2.png")],
                "phases": 2, "phase_ms": 700, "flags": {"bank": 300, "automap": 0x28}})
objects.append({"id": 111, "name": "deep water", "frames":
                [art("dngn/water/deep_water.png"), art("dngn/water/deep_water2.png")],
                "phases": 2, "phase_ms": 700, "flags": {"bank": 0, "unpass": True,
                                                         "unmove": True, "automap": 0x28}})
# walls
for i in range(4):
    obj(200 + i, "stone wall", f"dngn/wall/stone2_gray{i}.png", unpass=True, unmove=True,
        unsight=True, bottom=True, automap=0x56)
obj(210, "brick wall", "dngn/wall/brick_brown0.png", unpass=True, unmove=True, unsight=True,
    bottom=True, automap=0x79)
# nature
obj(300, "tree", "dngn/trees/tree1_yellow.png", unpass=True, unmove=True, unsight=False,
    automap=0x0C)
obj(301, "tree", "dngn/trees/tree2_red.png", unpass=True, unmove=True, automap=0x0C)
# doors (closed blocks, open passes)
obj(400, "closed door", "dngn/doors/closed_door.png", unpass=True, unmove=True, unsight=True,
    usable=True, bottom=True)
obj(401, "open door", "dngn/doors/open_door.png", unmove=True, usable=True, bottom=True)
obj(410, "teleporter", "dngn/teleporter.png", unmove=True)
# items
obj(1000, "gold coin", "item/gold/01.png", take=True, cumulative=True)
obj(1001, "silver coin", "item/gold/03.png", take=True, cumulative=True)
obj(1010, "health potion", "item/potion/ruby.png", take=True, cumulative=True, usable=True,
    multiuse=True)
obj(1011, "mana potion", "item/potion/brilliant_blue.png", take=True, cumulative=True,
    usable=True, multiuse=True)
obj(1020, "club", "item/weapon/club.png", take=True, clothes=6)
obj(1021, "dagger", "item/weapon/dagger.png", take=True, clothes=6)
obj(1030, "leather armor", "item/armour/leather_armour1.png", take=True, clothes=4)
obj(1031, "leather boots", "item/armour/boots1_brown.png", take=True, clothes=8)
obj(1040, "backpack", "item/misc/misc_box.png", take=True, container=True, clothes=3)
obj(1050, "corpse", "mon/undead/zombies/zombie_rat.png", corpse=True, container=True,
    unmove=False)


def outfit(id_, name, rel):
    # placeholder: the CC0 creature art faces one way, so all 4 directions share it.
    # Replace with 4-direction walk sheets later; ids and server data won't change.
    f = art(rel)
    outfits.append({"id": id_, "name": name, "patterns": [4, 1, 1],
                    "idle": [f] * 4, "moving": [f] * 4, "flags": {}})


outfit(1, "human male", "player/base/human_m.png")
outfit(2, "human female", "player/base/human_f.png")
outfit(100, "rat", "mon/undead/zombies/zombie_rat.png")
outfit(101, "goblin", "mon/goblin.png")
outfit(102, "orc", "mon/orc.png")
outfit(103, "jackal", "mon/animals/jackal.png")
outfit(104, "bat", "mon/animals/bat.png")

# server-side item properties -> generated into items.xml (tools/mapgen/items_xml.py)
SERVER = {
    1000: {"article": "a", "attrs": {"primarytype": "valuables", "weight": 10, "worth": 1}},
    1001: {"article": "a", "attrs": {"primarytype": "valuables", "weight": 10, "worth": 100}},
    1010: {"article": "a", "attrs": {"primarytype": "potions", "weight": 180}},
    1011: {"article": "a", "attrs": {"primarytype": "potions", "weight": 180}},
    1020: {"article": "a", "attrs": {"primarytype": "club weapons", "weaponType": "club",
                                      "attack": 7, "defense": 7, "weight": 2500},
           "script": ("moveevent;weapon", {"weaponType": "club", "slot": "hand"})},
    1021: {"article": "a", "attrs": {"primarytype": "sword weapons", "weaponType": "sword",
                                      "attack": 8, "defense": 6, "weight": 950},
           "script": ("moveevent;weapon", {"weaponType": "sword", "slot": "hand"})},
    1030: {"article": "a", "attrs": {"primarytype": "armors", "armor": 4, "weight": 6000},
           "script": ("moveevent", {"slot": "armor"})},
    1031: {"article": "a pair of", "attrs": {"primarytype": "boots", "armor": 1, "weight": 900},
           "script": ("moveevent", {"slot": "feet"})},
    1040: {"article": "a", "attrs": {"primarytype": "containers", "containersize": 20,
                                      "weight": 1800}},
    1050: {"article": "a", "attrs": {"containersize": 6, "decayTo": 0, "duration": 120,
                                      "corpseType": "blood"}},
}
for o in objects:
    if o["id"] in SERVER:
        o["server"] = SERVER[o["id"]]

manifest = {"objects": objects, "outfits": outfits, "effects": [], "missiles": [],
            "special": {"gold_coin_id": 1000}}
(ROOT / "assets" / "manifest.json").write_text(json.dumps(manifest, indent=1))
print(f"{len(objects)} objects, {len(outfits)} outfits")
