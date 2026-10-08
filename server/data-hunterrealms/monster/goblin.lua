local mType = Game.createMonsterType("Goblin")
local monster = {}

monster.description = "a goblin"
monster.experience = 25
monster.outfit = { lookType = 101, lookHead = 0, lookBody = 0, lookLegs = 0, lookFeet = 0, lookAddons = 0, lookMount = 0 }

monster.health = 70
monster.maxHealth = 70
monster.race = "blood"
monster.corpse = 1050
monster.speed = 85
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
	{ text = "Shiny!", yell = false },
	{ text = "Me find loot!", yell = false },
}

monster.loot = {
	{ id = 1000, chance = 70000, maxCount = 10 },
	{ id = 1021, chance = 8000, maxCount = 1 },
	{ id = 1010, chance = 5000, maxCount = 1 },
}

monster.attacks = {
	{ name = "melee", interval = 2000, chance = 100, minDamage = 0, maxDamage = -20 },
}

monster.defenses = { defense = 6, armor = 6 }

monster.elements = {}
monster.immunities = {}

mType:register(monster)
