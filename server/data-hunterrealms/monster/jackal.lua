local mType = Game.createMonsterType("Jackal")
local monster = {}

monster.description = "a jackal"
monster.experience = 12
monster.outfit = { lookType = 103, lookHead = 0, lookBody = 0, lookLegs = 0, lookFeet = 0, lookAddons = 0, lookMount = 0 }

monster.health = 45
monster.maxHealth = 45
monster.race = "blood"
monster.corpse = 61050
monster.speed = 100
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
	{ text = "Yip!", yell = false },
}

monster.loot = {
	{ id = 3031, chance = 50000, maxCount = 6 },
	{ id = 61031, chance = 3000, maxCount = 1 },
}

monster.attacks = {
	{ name = "melee", interval = 2000, chance = 100, minDamage = 0, maxDamage = -14 },
}

monster.defenses = { defense = 4, armor = 4 }

monster.elements = {}
monster.immunities = {}

mType:register(monster)
