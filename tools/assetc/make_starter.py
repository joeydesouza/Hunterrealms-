#!/usr/bin/env python3
"""Copy the starter CC0 tiles into assets/art and write assets/manifest.json.

Item id ranges (ours, not Tibia's):
  60100 grounds   60200 walls/borders   60300 nature/decor   60400 doors
  61000+ items    outfits 1+ (players)   100+ (monsters)
Our content lives at 60000+ so it never collides with ids the server core's
scripts register (those use the original 1-50000 range).
Engine-reserved ids (coins, containers, corpses, splashes) keep the numbers the
server core hard-codes; only the art is ours.
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
obj(60100, "grass", "dngn/floor/grass/grass0.png", bank=150, automap=0x18)
obj(60101, "grass", "dngn/floor/grass/grass1.png", bank=150, automap=0x18)
obj(60102, "dirt", "dngn/floor/dirt0.png", bank=160, automap=0x79)
obj(60103, "cobblestone", "dngn/floor/pebble_brown0.png", bank=120, automap=0x56)
obj(60104, "sand", "dngn/floor/sand1.png", bank=170, automap=0xCF)
obj(60105, "wooden floor", "dngn/floor/limestone0.png", bank=120, automap=0x79)
objects.append({"id": 60110, "name": "shallow water", "frames":
                [art("dngn/water/shallow_water.png"), art("dngn/water/shallow_water2.png")],
                "phases": 2, "phase_ms": 700, "flags": {"bank": 300, "automap": 0x28}})
objects.append({"id": 60111, "name": "deep water", "frames":
                [art("dngn/water/deep_water.png"), art("dngn/water/deep_water2.png")],
                "phases": 2, "phase_ms": 700, "flags": {"bank": 0, "unpass": True,
                                                         "unmove": True, "automap": 0x28}})
# walls
for i in range(4):
    obj(60200 + i, "stone wall", f"dngn/wall/stone2_gray{i}.png", unpass=True, unmove=True,
        unsight=True, bottom=True, automap=0x56)
obj(60210, "brick wall", "dngn/wall/brick_brown0.png", unpass=True, unmove=True, unsight=True,
    bottom=True, automap=0x79)
# nature
obj(60300, "tree", "dngn/trees/tree1_yellow.png", unpass=True, unmove=True, unsight=False,
    automap=0x0C)
obj(60301, "tree", "dngn/trees/tree2_red.png", unpass=True, unmove=True, automap=0x0C)
# doors (closed blocks, open passes)
obj(60400, "closed door", "dngn/doors/closed_door.png", unpass=True, unmove=True, unsight=True,
    usable=True, bottom=True)
obj(60401, "open door", "dngn/doors/open_door.png", unmove=True, usable=True, bottom=True)
obj(60410, "teleporter", "dngn/teleporter.png", unmove=True)
# items
# --- engine-reserved ids: the server core refers to these numbers directly ---
obj(3031, "gold coin", "item/gold/01.png", take=True, cumulative=True)
obj(3035, "platinum coin", "item/gold/03.png", take=True, cumulative=True)
obj(3043, "crystal coin", "item/gold/16.png", take=True, cumulative=True)
obj(2853, "bag", "item/misc/misc_box.png", take=True, container=True, clothes=3)
obj(2854, "backpack", "item/misc/misc_box.png", take=True, container=True, clothes=3)
for cid, cname in [(3497, "locker"), (3502, "depot chest"), (12902, "your inbox"),
                   (12903, "market"), (23396, "your store inbox"), (28750, "supply stash"),
                   (19202, "reward container")]:
    obj(cid, cname, "item/misc/misc_box.png", container=True, unmove=True)
obj(3503, "parcel", "item/misc/misc_box.png", take=True, container=True)
obj(3504, "stamped parcel", "item/misc/misc_box.png", take=True, container=True)
obj(3505, "letter", "item/scroll/i-blinking.png", take=True)
obj(3506, "stamped letter", "item/scroll/i-blinking.png", take=True)
obj(2886, "blood", "misc/blood/blood_red01.png", liquidpool=True, unmove=True)
obj(2889, "blood", "misc/blood/blood_red02.png", liquidpool=True, unmove=True)
obj(4240, "dead human", "misc/blood/blood_red00.png", container=True, corpse=True, player_corpse=True)
obj(4247, "dead human", "misc/blood/blood_red03.png", container=True, corpse=True, player_corpse=True)
obj(61010, "health potion", "item/potion/ruby.png", take=True, cumulative=True, usable=True,
    multiuse=True)
obj(61011, "mana potion", "item/potion/brilliant_blue.png", take=True, cumulative=True,
    usable=True, multiuse=True)
obj(61020, "club", "item/weapon/club.png", take=True, clothes=6)
obj(61021, "dagger", "item/weapon/dagger.png", take=True, clothes=6)
obj(61030, "leather armor", "item/armour/leather_armour1.png", take=True, clothes=4)
obj(61031, "leather boots", "item/armour/boots1_brown.png", take=True, clothes=8)
obj(61050, "corpse", "mon/undead/zombies/zombie_rat.png", corpse=True, container=True,
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
    3031: {"article": "a", "attrs": {"primarytype": "valuables", "weight": 10, "worth": 1}},
    3035: {"article": "a", "attrs": {"primarytype": "valuables", "weight": 10, "worth": 100}},
    3043: {"article": "a", "attrs": {"primarytype": "valuables", "weight": 10, "worth": 10000}},
    2853: {"article": "a", "attrs": {"primarytype": "containers", "containersize": 8, "weight": 800}},
    2854: {"article": "a", "attrs": {"primarytype": "containers", "containersize": 20,
                                      "weight": 1800}},
    3497: {"article": "a", "attrs": {"type": "depot", "containersize": 30}},
    3502: {"article": "a", "attrs": {"containersize": 30}},
    12902: {"attrs": {"containersize": 30}},
    12903: {"attrs": {"type": "container"}},
    23396: {"attrs": {"containersize": 30}},
    28750: {"article": "a", "attrs": {"type": "container"}},
    19202: {"article": "a", "attrs": {"containersize": 30}},
    3503: {"article": "a", "attrs": {"type": "container", "containersize": 10, "weight": 1800}},
    3504: {"article": "a", "attrs": {"type": "container", "containersize": 10, "weight": 1800}},
    3505: {"article": "a", "attrs": {"type": "mailbox", "weight": 50}},
    3506: {"article": "a", "attrs": {"weight": 50}},
    2886: {"attrs": {"type": "splash", "duration": 30, "decayTo": 0}},
    2889: {"attrs": {"type": "splash", "duration": 30, "decayTo": 0}},
    4240: {"article": "a", "attrs": {"containersize": 10, "duration": 300, "decayTo": 0,
                                      "corpseType": "blood"}},
    4247: {"article": "a", "attrs": {"containersize": 10, "duration": 300, "decayTo": 0,
                                      "corpseType": "blood"}},
    61010: {"article": "a", "attrs": {"primarytype": "potions", "weight": 180}},
    61011: {"article": "a", "attrs": {"primarytype": "potions", "weight": 180}},
    61020: {"article": "a", "attrs": {"primarytype": "club weapons", "weaponType": "club",
                                      "attack": 7, "defense": 7, "weight": 2500},
           "script": ("moveevent;weapon", {"weaponType": "club", "slot": "hand"})},
    61021: {"article": "a", "attrs": {"primarytype": "sword weapons", "weaponType": "sword",
                                      "attack": 8, "defense": 6, "weight": 950},
           "script": ("moveevent;weapon", {"weaponType": "sword", "slot": "hand"})},
    61030: {"article": "a", "attrs": {"primarytype": "armors", "armor": 4, "weight": 6000},
           "script": ("moveevent", {"slot": "armor"})},
    61031: {"article": "a pair of", "attrs": {"primarytype": "boots", "armor": 1, "weight": 900},
           "script": ("moveevent", {"slot": "feet"})},
    61050: {"article": "a", "attrs": {"containersize": 6, "decayTo": 0, "duration": 120,
                                      "corpseType": "blood"}},
}
for o in objects:
    if o["id"] in SERVER:
        o["server"] = SERVER[o["id"]]

# Magic effects (ids 1-303) and missiles (1-62) are referenced by number all over the
# server core, so every id must exist. Placeholder art cycles through CC0 effect tiles;
# replace individual ids with proper animations over time.
fx_dir = SRC / "effect"
clouds = sorted(p.name for p in fx_dir.glob("cloud_*.png"))
bolts = sorted(p.name for p in fx_dir.glob("bolt*.png")) + sorted(p.name for p in fx_dir.glob("arrow*.png"))
effects = [{"id": i, "frames": [art(f"effect/{clouds[i % len(clouds)]}")], "flags": {}}
           for i in range(1, 304)]
missiles = []
for i in range(1, 63):
    f = art(f"effect/{bolts[i % len(bolts)]}")
    missiles.append({"id": i, "patterns": [3, 3, 1], "frames": [f] * 9, "flags": {}})

manifest = {"objects": objects, "outfits": outfits, "effects": effects, "missiles": missiles,
            "special": {"gold_coin_id": 3031, "platinum_coin_id": 3035, "crystal_coin_id": 3043}}
(ROOT / "assets" / "manifest.json").write_text(json.dumps(manifest, indent=1))
print(f"{len(objects)} objects, {len(outfits)} outfits")
