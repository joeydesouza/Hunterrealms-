#!/usr/bin/env python3
"""Generate monster scripts for the datapack from a compact table.

Usage: monsters.py <datapack monster dir>
lookType = outfit id in assets/manifest.json; loot ids are ours.
"""
import sys
from pathlib import Path

GOLD, HP_POT, MP_POT, CLUB, DAGGER, LEATHER, BOOTS = 3031, 61010, 61011, 61020, 61021, 61030, 61031
CORPSE = 61050

# name, lookType, hp, exp, speed, maxHit, armor, loot[(id, chance/100000, maxCount)], voices
MONSTERS = [
    ("Rat", 100, 20, 5, 70, 8, 2, [(GOLD, 60000, 4)], ["Meep!"]),
    ("Bat", 104, 30, 10, 110, 10, 2, [(GOLD, 40000, 3)], ["Flap!"]),
    ("Jackal", 103, 45, 12, 100, 14, 4, [(GOLD, 50000, 6), (BOOTS, 3000, 1)], ["Yip!"]),
    ("Goblin", 101, 70, 25, 85, 20, 6,
     [(GOLD, 70000, 10), (DAGGER, 8000, 1), (HP_POT, 5000, 1)], ["Shiny!", "Me find loot!"]),
    ("Orc", 102, 120, 45, 90, 32, 10,
     [(GOLD, 80000, 18), (CLUB, 10000, 1), (LEATHER, 6000, 1), (HP_POT, 8000, 1),
      (MP_POT, 6000, 1)], ["Grak brak!", "Orc smash!"]),
]

TEMPLATE = '''local mType = Game.createMonsterType("{name}")
local monster = {{}}

monster.description = "{article} {lname}"
monster.experience = {exp}
monster.outfit = {{ lookType = {look}, lookHead = 0, lookBody = 0, lookLegs = 0, lookFeet = 0, lookAddons = 0, lookMount = 0 }}

monster.health = {hp}
monster.maxHealth = {hp}
monster.race = "blood"
monster.corpse = {corpse}
monster.speed = {speed}
monster.manaCost = 0

monster.changeTarget = {{ interval = 4000, chance = 10 }}
monster.strategiesTarget = {{ nearest = 100 }}

monster.flags = {{
	summonable = false,
	attackable = true,
	hostile = true,
	convinceable = false,
	pushable = true,
	rewardBoss = false,
	illusionable = false,
	canPushItems = false,
	canPushCreatures = false,
	staticAttackChance = 90,
	targetDistance = 1,
	runHealth = 0,
	healthHidden = false,
	isBlockable = false,
	canWalkOnEnergy = false,
	canWalkOnFire = false,
	canWalkOnPoison = false,
}}

monster.light = {{ level = 0, color = 0 }}

monster.voices = {{
	interval = 5000,
	chance = 10,
{voices}
}}

monster.loot = {{
{loot}
}}

monster.attacks = {{
	{{ name = "melee", interval = 2000, chance = 100, minDamage = 0, maxDamage = -{maxhit} }},
}}

monster.defenses = {{ defense = {armor}, armor = {armor} }}

monster.elements = {{}}
monster.immunities = {{}}

mType:register(monster)
'''


def main():
    out = Path(sys.argv[1])
    out.mkdir(parents=True, exist_ok=True)
    for name, look, hp, exp, speed, maxhit, armor, loot, voices in MONSTERS:
        text = TEMPLATE.format(
            name=name, lname=name.lower(), article="an" if name[0] in "AEIOU" else "a",
            exp=exp, look=look, hp=hp, corpse=CORPSE, speed=speed, maxhit=maxhit, armor=armor,
            voices="\n".join(f'\t{{ text = "{v}", yell = false }},' for v in voices),
            loot="\n".join(f"\t{{ id = {i}, chance = {c}, maxCount = {n} }}," for i, c, n in loot))
        (out / f"{name.lower()}.lua").write_text(text)
    print(f"{len(MONSTERS)} monsters -> {out}")


if __name__ == "__main__":
    main()
