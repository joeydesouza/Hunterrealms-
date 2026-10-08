local mType = Game.createMonsterType("Bat")
local monster = {}

monster.description = "a bat"
monster.experience = 10
monster.outfit = { lookType = 104, lookHead = 0, lookBody = 0, lookLegs = 0, lookFeet = 0, lookAddons = 0, lookMount = 0 }

monster.health = 30
monster.maxHealth = 30
monster.race = "blood"
monster.corpse = 1050
monster.speed = 110
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
	{ text = "Flap!", yell = false },
}

monster.loot = {
	{ id = 1000, chance = 40000, maxCount = 3 },
}

monster.attacks = {
	{ name = "melee", interval = 2000, chance = 100, minDamage = 0, maxDamage = -10 },
}

monster.defenses = { defense = 2, armor = 2 }

monster.elements = {}
monster.immunities = {}

mType:register(monster)
