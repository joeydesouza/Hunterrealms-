-- Dev seed: removes the engine's sample characters (they use Tibia outfits)
-- and adds a test account. Login: account "test", password "test123".
DELETE FROM players WHERE account_id = 1;
INSERT INTO accounts (name, password, email, type, premdays, lastday, creation)
VALUES ('test', SHA1('test123'), 'test@hunterrealms.local', 1, 0, 0, UNIX_TIMESTAMP())
ON DUPLICATE KEY UPDATE password = VALUES(password);
INSERT INTO players (name, group_id, account_id, level, vocation, health, healthmax, experience,
  lookbody, lookfeet, lookhead, looklegs, looktype, maglevel, mana, manamax, manaspent, town_id,
  posx, posy, posz, conditions, cap, sex)
SELECT 'Hunter', 1, id, 8, 0, 185, 185, 4200, 0, 0, 0, 0, 1, 0, 90, 90, 0, 1,
  1000, 993, 7, '', 470, 1 FROM accounts WHERE name = 'test'
ON DUPLICATE KEY UPDATE posx = 1000, posy = 993, posz = 7, looktype = 1, town_id = 1;
