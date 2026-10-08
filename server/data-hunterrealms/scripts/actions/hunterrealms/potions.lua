-- Hunter Realms potions (ids from assets/manifest.json).
local potions = {
	[61010] = { health = { 60, 90 } }, -- health potion
	[61011] = { mana = { 40, 70 } }, -- mana potion
}

local potion = Action()

function potion.onUse(player, item, fromPosition, target, toPosition, isHotkey)
	if not target or (type(target) == "userdata" and not target:isPlayer()) then
		target = player
	end

	local cfg = potions[item:getId()]
	if not cfg then
		return false
	end

	if cfg.health then
		doTargetCombatHealth(player, target, COMBAT_HEALING, cfg.health[1], cfg.health[2], CONST_ME_MAGIC_BLUE)
	end
	if cfg.mana then
		doTargetCombatMana(0, target, cfg.mana[1], cfg.mana[2], CONST_ME_MAGIC_BLUE)
	end
	target:say("Aaaah...", MESSAGE_POTION)
	item:remove(1)
	return true
end

for id in pairs(potions) do
	potion:id(id)
end
potion:register()
