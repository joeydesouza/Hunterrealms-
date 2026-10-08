-- Hunter Realms starter kit (replaces the engine's Tibia-specific version).
-- Item ids: see assets/manifest.json.
local equipment = {
	61020, -- club
	61030, -- leather armor
	61031, -- leather boots
}

local backpackItems = {
	{ 61010, 10 }, -- health potion
	{ 61011, 5 }, -- mana potion
	{ 3031, 50 }, -- gold coin
}

local sendFirstItems = CreatureEvent("SendFirstItems")

function sendFirstItems.onLogin(player)
	if player:getLastLoginSaved() ~= 0 then
		return true
	end

	for _, itemId in ipairs(equipment) do
		player:addItem(itemId, 1)
	end

	local backpack = player:addItem(2854)
	if backpack then
		for _, entry in ipairs(backpackItems) do
			backpack:addItem(entry[1], entry[2])
		end
	end
	return true
end

sendFirstItems:register()
