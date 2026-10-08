// Hunter Realms web service:
//   POST /login         - the game client's HTTP login protocol (character list)
//   POST /api/register  - create an account + first character (used by the app)
//   GET  /health        - liveness check
import express from "express";
import { fileURLToPath } from "node:url";
import mysql from "mysql2/promise";
import { hashPassword, verifyPassword } from "./password.js";

const cfg = {
  port: Number(process.env.PORT || 8080),
  db: {
    host: process.env.DB_HOST || "127.0.0.1",
    port: Number(process.env.DB_PORT || 3306),
    user: process.env.DB_USER || "hunter",
    password: process.env.DB_PASSWORD || "hunter",
    database: process.env.DB_NAME || "hunterrealms",
  },
  world: {
    name: process.env.WORLD_NAME || "Hunter Realms",
    host: process.env.GAME_HOST || "127.0.0.1",
    port: Number(process.env.GAME_PORT || 7172),
    location: process.env.WORLD_LOCATION || "USA",
  },
  // new characters start in Hunter's Rest temple (see tools/mapgen/world.py)
  start: { town: 1, x: 1000, y: 993, z: 7 },
};

export function createApp(pool) {
  const app = express();
  app.use(express.json({ limit: "16kb" }));

  app.use(express.static(fileURLToPath(new URL("../public", import.meta.url))));
  app.get("/health", (_req, res) => res.json({ ok: true }));

  app.post(["/login", "/login.php"], async (req, res) => {
    const body = req.body || {};
    try {
      switch (body.type) {
        case "cacheinfo": {
          const [[row]] = await pool.query("SELECT COUNT(*) AS n FROM players_online");
          return res.json({ playersonline: row.n, twitchstreams: 0, twitchviewer: 0, gamingyoutubestreams: 0, gamingyoutubeviewer: 0 });
        }
        case "eventschedule":
          return res.json({ eventlist: [], lastupdatetimestamp: Math.floor(Date.now() / 1000) });
        case "boostedcreature":
          return res.json({ boostedcreature: false, raceid: 0 });
        case "login":
          return res.json(await login(pool, body));
        default:
          return res.json({ errorCode: 3, errorMessage: "Unsupported request." });
      }
    } catch (err) {
      console.error("[login]", err);
      return res.json({ errorCode: 2, errorMessage: "Login server error, try again shortly." });
    }
  });

  app.post("/api/register", async (req, res) => {
    try {
      const result = await register(pool, req.body || {});
      res.status(result.ok ? 201 : 400).json(result);
    } catch (err) {
      console.error("[register]", err);
      res.status(500).json({ ok: false, error: "Server error." });
    }
  });

  return app;
}

async function login(pool, { email, password }) {
  const fail = { errorCode: 3, errorMessage: "Email or password is not correct." };
  if (!email || !password) return fail;
  const [[account]] = await pool.query(
    "SELECT id, password, premdays, lastday FROM accounts WHERE email = ? LIMIT 1", [email]);
  if (!account || !(await verifyPassword(password, account.password))) return fail;

  const [chars] = await pool.query(
    `SELECT name, level, sex, vocation, looktype, lookhead, lookbody, looklegs, lookfeet, lookaddons FROM players WHERE account_id = ? AND deletion = 0 ORDER BY name`, [account.id]);
  const now = Math.floor(Date.now() / 1000);
  const premiumUntil = account.lastday > now ? account.lastday : 0;
  const w = cfg.world;
  return {
    session: {
      // the game server is configured with authType = "password" and expects "email\npassword"
      sessionkey: `${email}\n${password}`,
      lastlogintime: 0, ispremium: premiumUntil > now, premiumuntil: premiumUntil,
      status: "active", returnernotification: false, showrewardnews: false, isreturner: false,
      fpstracking: false, optiontracking: false, tournamentticketpurchasestate: 0,
      emailcoderequest: false,
    },
    playdata: {
      worlds: [{
        id: 0, name: w.name, externaladdress: w.host, externalport: w.port,
        externaladdressprotected: w.host, externalportprotected: w.port,
        externaladdressunprotected: w.host, externalportunprotected: w.port,
        previewstate: 0, location: w.location, anticheatprotection: false, pvptype: 1,
        istournamentworld: false, restrictedstore: false, currenttournamentphase: 2,
      }],
      characters: chars.map((c) => ({
        worldid: 0, name: c.name, ismale: c.sex === 1, tutorial: false, level: c.level,
        vocation: VOCATIONS[c.vocation] || "None", outfitid: c.looktype, headcolor: c.lookhead,
        torsocolor: c.lookbody, legscolor: c.looklegs, detailcolor: c.lookfeet,
        addonsflags: c.lookaddons, ishidden: false, istournamentparticipant: false,
        ismaincharacter: false, dailyrewardstate: 0, remainingdailytournamentplaytime: 0,
      })),
    },
  };
}

const VOCATIONS = ["None", "Sorcerer", "Druid", "Paladin", "Knight", "Master Sorcerer",
  "Elder Druid", "Royal Paladin", "Elite Knight"];

export function validateRegistration({ email, password, characterName, sex }) {
  if (typeof email !== "string" || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email) || email.length > 255)
    return "Enter a valid email address.";
  if (typeof password !== "string" || password.length < 8 || password.length > 64)
    return "Password must be 8-64 characters.";
  if (typeof characterName !== "string" || !/^[A-Z][a-z]+( [A-Z][a-z]+){0,2}$/.test(characterName)
      || characterName.length < 3 || characterName.length > 25)
    return "Character name: 3-25 letters, each word capitalized (e.g. \"Swift Arrow\").";
  if (sex !== 0 && sex !== 1) return "Choose male or female.";
  return null;
}

async function register(pool, body) {
  const sex = Number(body.sex ?? 1);
  const input = { ...body, sex };
  const error = validateRegistration(input);
  if (error) return { ok: false, error };
  const conn = await pool.getConnection();
  try {
    await conn.beginTransaction();
    const [[dupMail]] = await conn.query("SELECT id FROM accounts WHERE email = ?", [input.email]);
    if (dupMail) { await conn.rollback(); return { ok: false, error: "That email is already registered." }; }
    const [[dupName]] = await conn.query("SELECT id FROM players WHERE name = ?", [input.characterName]);
    if (dupName) { await conn.rollback(); return { ok: false, error: "That character name is taken." }; }
    const hash = await hashPassword(input.password);
    // accounts.name must be unique; derive it from the email
    const [acc] = await conn.query(
      "INSERT INTO accounts (name, password, email, type, premdays, lastday, creation) VALUES (?, ?, ?, 1, 0, 0, UNIX_TIMESTAMP())",
      [input.email, hash, input.email]);
    const s = cfg.start;
    await conn.query(
      `INSERT INTO players (name, group_id, account_id, level, vocation, health, healthmax, experience,
         lookbody, lookfeet, lookhead, looklegs, looktype, maglevel, mana, manamax, manaspent,
         town_id, posx, posy, posz, conditions, cap, sex)
       VALUES (?, 1, ?, 1, 0, 150, 150, 0, 0, 0, 0, 0, ?, 0, 50, 50, 0, ?, ?, ?, ?, '', 400, ?)`,
      [input.characterName, acc.insertId, sex === 1 ? 1 : 2, s.town, s.x, s.y, s.z, sex]);
    await conn.commit();
    return { ok: true };
  } catch (err) {
    await conn.rollback();
    throw err;
  } finally {
    conn.release();
  }
}

if (import.meta.url === `file://${process.argv[1]}`) {
  const pool = mysql.createPool({ ...cfg.db, connectionLimit: 10 });
  createApp(pool).listen(cfg.port, () =>
    console.log(`Hunter Realms web on :${cfg.port} (world ${cfg.world.host}:${cfg.world.port})`));
}
