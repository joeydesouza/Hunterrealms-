import { test } from "node:test";
import assert from "node:assert/strict";
import { hashPassword, verifyPassword } from "../src/password.js";
import { validateRegistration } from "../src/server.js";

test("password hash round-trips and rejects wrong passwords", async () => {
  const stored = await hashPassword("hunter123");
  assert.match(stored, /^\$[A-Za-z0-9+/]+\$[A-Za-z0-9+/]+$/);
  assert.equal(await verifyPassword("hunter123", stored), true);
  assert.equal(await verifyPassword("hunter124", stored), false);
});

test("registration validation", () => {
  const ok = { email: "a@b.co", password: "longenough", characterName: "Swift Arrow", sex: 1 };
  assert.equal(validateRegistration(ok), null);
  assert.ok(validateRegistration({ ...ok, email: "nope" }));
  assert.ok(validateRegistration({ ...ok, password: "short" }));
  assert.ok(validateRegistration({ ...ok, characterName: "lowercase" }));
  assert.ok(validateRegistration({ ...ok, sex: 3 }));
});
