-- Hunter Realms hunt assistant.
-- Big on-screen toggles for: auto heal (health potion), auto mana (mana potion),
-- auto attack (nearest monster) and an attack-spell rotation. Settings are saved
-- per character. Item ids come from assets/manifest.json.

local HEALTH_POTION = 61010
local MANA_POTION = 61011
local TICK_MS = 200
local POTION_EXHAUST_MS = 1000
local ATTACK_RANGE = 7

local defaults = {
  heal = false, mana = false, attack = false, spells = false,
  healAt = 60, manaAt = 40,
  spellList = "",          -- "words, minMana, seconds" per line
}

local bar, settingsWindow, tickEvent
local buttons = {}
local cfg = {}
local nextPotionAt = 0
local spellNextAt = {}

local function settingsKey()
  local player = g_game.getLocalPlayer()
  return "hr_assistant_" .. (player and player:getName() or "default")
end

local function load()
  local saved = g_settings.getNode(settingsKey()) or {}
  cfg = {}
  for k, v in pairs(defaults) do
    if saved[k] == nil then cfg[k] = v else cfg[k] = saved[k] end
  end
  -- toggles always start off after login; settings persist
  cfg.heal, cfg.mana, cfg.attack, cfg.spells = false, false, false, false
end

local function save()
  g_settings.setNode(settingsKey(), cfg)
  g_settings.save()
end

-- "exori, 20, 4" -> { words = "exori", minMana = 20, every = 4000 }
local function parseSpells(text)
  local list = {}
  for line in (text or ""):gmatch("[^\n]+") do
    local words, minMana, secs = line:match("^%s*(.-)%s*,%s*(%d+)%s*,%s*([%d%.]+)%s*$")
    if words and words ~= "" then
      list[#list + 1] = { words = words, minMana = tonumber(minMana), every = math.floor(tonumber(secs) * 1000) }
    end
  end
  return list
end

local function percent(value, max)
  if not max or max <= 0 then return 100 end
  return value * 100 / max
end

local function refreshButtons()
  local labels = { heal = "Heal", mana = "Mana", attack = "Attack", spells = "Spells" }
  for key, button in pairs(buttons) do
    button:setText(labels[key] .. "\n" .. (cfg[key] and "ON" or "off"))
    button:setOn(cfg[key])
    button:setColor(cfg[key] and "#7CFC7C" or "#BBBBBB")
  end
end

local function nearestMonster(player)
  local pos = player:getPosition()
  local best, bestDist
  for _, creature in ipairs(g_map.getSpectatorsInRange(pos, false, ATTACK_RANGE, ATTACK_RANGE)) do
    if creature:isMonster() and creature:getHealthPercent() > 0 then
      local cpos = creature:getPosition()
      local dist = math.max(math.abs(cpos.x - pos.x), math.abs(cpos.y - pos.y))
      if not best or dist < bestDist then
        best, bestDist = creature, dist
      end
    end
  end
  return best
end

local function tick()
  if not g_game.isOnline() then return end
  local player = g_game.getLocalPlayer()
  if not player then return end
  local now = g_clock.millis()

  -- 1. survival first: health, then mana
  if now >= nextPotionAt then
    if cfg.heal and percent(player:getHealth(), player:getMaxHealth()) < cfg.healAt
        and player:getInventoryCount(HEALTH_POTION, 0) > 0 then
      g_game.useInventoryItemWith(HEALTH_POTION, player)
      nextPotionAt = now + POTION_EXHAUST_MS
      return
    end
    if cfg.mana and percent(player:getMana(), player:getMaxMana()) < cfg.manaAt
        and player:getInventoryCount(MANA_POTION, 0) > 0 then
      g_game.useInventoryItemWith(MANA_POTION, player)
      nextPotionAt = now + POTION_EXHAUST_MS
      return
    end
  end

  -- 2. keep a target
  if cfg.attack and not g_game.isAttacking() then
    local target = nearestMonster(player)
    if target then g_game.attack(target) end
  end

  -- 3. spell rotation while fighting
  if cfg.spells and g_game.isAttacking() then
    for _, spell in ipairs(parseSpells(cfg.spellList)) do
      if player:getMana() >= spell.minMana and now >= (spellNextAt[spell.words] or 0) then
        g_game.talk(spell.words)
        spellNextAt[spell.words] = now + spell.every
        break
      end
    end
  end
end

local function toggle(key)
  cfg[key] = not cfg[key]
  refreshButtons()
end

function showSettings()
  if not settingsWindow then
    settingsWindow = g_ui.createWidget("HRSettings", rootWidget)
  end
  settingsWindow:getChildById("healAt"):setText(tostring(cfg.healAt))
  settingsWindow:getChildById("manaAt"):setText(tostring(cfg.manaAt))
  settingsWindow:getChildById("spells"):setText(cfg.spellList or "")
  settingsWindow:show()
  settingsWindow:raise()
  settingsWindow:focus()
end

function hideSettings()
  if settingsWindow then settingsWindow:hide() end
end

function saveSettings()
  local function clampPct(text, fallback)
    local n = tonumber(text)
    if not n then return fallback end
    return math.max(1, math.min(99, math.floor(n)))
  end
  cfg.healAt = clampPct(settingsWindow:getChildById("healAt"):getText(), cfg.healAt)
  cfg.manaAt = clampPct(settingsWindow:getChildById("manaAt"):getText(), cfg.manaAt)
  cfg.spellList = settingsWindow:getChildById("spells"):getText()
  save()
  hideSettings()
end

local function onGameStart()
  load()
  spellNextAt, nextPotionAt = {}, 0
  local mapPanel = modules.game_interface.getMapPanel()
  bar = g_ui.createWidget("HRBar", mapPanel)
  bar:addAnchor(AnchorTop, "parent", AnchorTop)
  bar:addAnchor(AnchorRight, "parent", AnchorRight)
  bar:setMarginTop(6)
  bar:setMarginRight(6)
  for _, key in ipairs({ "heal", "mana", "attack", "spells" }) do
    local button = g_ui.createWidget("HRToggle", bar)
    button.onClick = function() toggle(key) end
    buttons[key] = button
  end
  local gear = g_ui.createWidget("HRToggle", bar)
  gear:setText("Setup")
  gear.onClick = showSettings
  refreshButtons()
  tickEvent = cycleEvent(tick, TICK_MS)
end

local function onGameEnd()
  if tickEvent then removeEvent(tickEvent) tickEvent = nil end
  if bar then bar:destroy() bar = nil end
  buttons = {}
  hideSettings()
end

function init()
  g_ui.importStyle("hr_assistant")
  connect(g_game, { onGameStart = onGameStart, onGameEnd = onGameEnd })
  if g_game.isOnline() then onGameStart() end
end

function terminate()
  disconnect(g_game, { onGameStart = onGameStart, onGameEnd = onGameEnd })
  onGameEnd()
  if settingsWindow then settingsWindow:destroy() settingsWindow = nil end
end
