// Password hashing compatible with the game server's Argon2 check.
// The server looks for "$<base64 salt>$<base64 hash>" and re-hashes with argon2id
// using config.lua's memoryConst / temporaryConst / parallelism, so these must match.
import { argon2id } from "hash-wasm";
import { randomBytes } from "node:crypto";

export const ARGON = {
  memorySize: 1 << 16, // memoryConst = "1<<16" (KiB)
  iterations: 2,       // temporaryConst = 2
  parallelism: 2,      // parallelism = 2
  hashLength: 32,
};

export async function hashPassword(password) {
  const salt = randomBytes(16);
  const hash = await argon2id({ password, salt, ...ARGON, outputType: "binary" });
  return `$${salt.toString("base64").replace(/=+$/, "")}$${Buffer.from(hash).toString("base64").replace(/=+$/, "")}`;
}

export async function verifyPassword(password, stored) {
  const m = /\$([A-Za-z0-9+/]+)\$([A-Za-z0-9+/]+)/.exec(stored || "");
  if (!m) return false;
  const salt = Buffer.from(m[1], "base64");
  const expected = Buffer.from(m[2], "base64");
  const hash = Buffer.from(await argon2id({
    password, salt, ...ARGON, hashLength: expected.length, outputType: "binary",
  }));
  return hash.length === expected.length && hash.equals(expected);
}
