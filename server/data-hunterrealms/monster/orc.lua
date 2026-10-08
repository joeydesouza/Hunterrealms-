local mType = Game.createMonsterType("Orc")
local monster = {}

monster.description = "an orc"
monster.experience = 45
monster.outfit = { lookType = 102, lookHead = 0, lookBody = 0, lookLegs = 0, lookFeet = 0, lookAddons = 0, lookMount = 0 }

monster.health = 120
monster.maxHealth = 120
monster.race = "blood"
monster.corpse = 61050
monster.speed = 90
monster.manaCost = 0

monster.changeTarget = { interval = 4000, chance = 10 }
monster.strategiesTarget = { nearest = 100 }

monster.flags = {
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
}

monster.light = { level = 0, color = 0 }

monster.voices = {
	interval = 5000,
	chance = 10,
	{ text = "Grak brak!", yell = false },
	{ text = "Orc smash!", yell = false },
}

monster.loot = {
	{ id = 3031, chance = 80000, maxCount = 18 },
	{ id = 61020, chance = 10000, maxCount = 1 },
	{ id = 61030, chance = 6000, maxCount = 1 },
	{ id = 61010, chance = 8000, maxCount = 1 },
	{ id = 61011, chance = 6000, maxCount = 1 },
}

monster.attacks = {
	{ name = "melee", interval = 2000, chance = 100, minDamage = 0, maxDamage = -32 },
}

monster.defenses = { defense = 10, armor = 10 }

monster.elements = {}
monster.immunities = {}

mType:register(monster)
