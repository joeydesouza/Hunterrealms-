local npcName = "Mara"

local npcType = Game.createNpcType(npcName)
local npcConfig = {}

npcConfig.name = npcName
npcConfig.description = "Mara, the supplier of Hunter's Rest"

npcConfig.health = 100
npcConfig.maxHealth = npcConfig.health
npcConfig.walkInterval = 0
npcConfig.walkRadius = 0

npcConfig.outfit = { lookType = 2, lookHead = 0, lookBody = 0, lookLegs = 0, lookFeet = 0, lookAddons = 0 }

npcConfig.voices = {
	interval = 15000,
	chance = 25,
	{ text = "Potions! Fresh potions for brave hunters!" },
}

npcConfig.flags = { floorchange = false }

-- ids are ours: see assets/manifest.json
npcConfig.shop = {
	{ itemName = "health potion", clientId = 1010, buy = 25, sell = 5 },
	{ itemName = "mana potion", clientId = 1011, buy = 30, sell = 5 },
	{ itemName = "club", clientId = 1020, buy = 40, sell = 8 },
	{ itemName = "dagger", clientId = 1021, buy = 60, sell = 12 },
	{ itemName = "leather armor", clientId = 1030, buy = 120, sell = 25 },
	{ itemName = "leather boots", clientId = 1031, buy = 50, sell = 10 },
	{ itemName = "backpack", clientId = 1040, buy = 20 },
}

local keywordHandler = KeywordHandler:new()
local npcHandler = NpcHandler:new(keywordHandler)

npcType.onThink = function(npc, interval) npcHandler:onThink(npc, interval) end
npcType.onAppear = function(npc, creature) npcHandler:onAppear(npc, creature) end
npcType.onDisappear = function(npc, creature) npcHandler:onDisappear(npc, creature) end
npcType.onMove = function(npc, creature, fromPosition, toPosition) npcHandler:onMove(npc, creature, fromPosition, toPosition) end
npcType.onSay = function(npc, creature, type, message) npcHandler:onSay(npc, creature, type, message) end
npcType.onCloseChannel = function(npc, player) npcHandler:onCloseChannel(npc, player) end

npcType.onBuyItem = function(npc, player, itemId, subType, amount, ignore, inBackpacks, totalCost)
	npc:sellItem(player, itemId, amount, subType, 0, ignore, inBackpacks)
end
npcType.onSellItem = function(npc, player, itemId, subtype, amount, ignore, name, totalCost)
	player:sendTextMessage(MESSAGE_TRADE, string.format("Sold %ix %s for %i gold.", amount, name, totalCost))
end
npcType.onCheckItem = function(npc, player, clientId, subType) end

npcHandler:setMessage(MESSAGE_GREET, "Welcome, |PLAYERNAME|! Say {trade} to see my wares.")
npcHandler:setMessage(MESSAGE_FAREWELL, "Good hunting, |PLAYERNAME|.")
npcHandler:setMessage(MESSAGE_WALKAWAY, "Good hunting.")

npcHandler:addModule(FocusModule:new(), npcConfig.name, true, true, true)
npcType:register(npcConfig)
