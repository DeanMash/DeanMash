import assert from "node:assert/strict";
import { describe, it } from "node:test";
import {
  createMashtechSessionToken,
  isMashtechAuthed,
  verifyMashtechPassword,
} from "./auth";
import { averageRating } from "./ratings";

describe("Mashtech auth", () => {
  it("accepts valid password and session token", () => {
    process.env.MASHTECH_DASHBOARD_PASSWORD = "test-pass";
    assert.equal(verifyMashtechPassword("test-pass"), true);
    assert.equal(verifyMashtechPassword("wrong"), false);
    const token = createMashtechSessionToken();
    assert.equal(isMashtechAuthed(token), true);
    assert.equal(isMashtechAuthed("bad.token"), false);
  });
});

describe("Average rating", () => {
  it("computes shop average from pulses", () => {
    const r = averageRating([
      { rating: 5 },
      { rating: 4 },
      { rating: 5 },
    ]);
    assert.equal(r.average, 4.7);
    assert.equal(r.count, 3);
    assert.match(r.starsLabel, /4\.7/);
  });

  it("handles no ratings", () => {
    const r = averageRating([]);
    assert.equal(r.average, null);
    assert.equal(r.count, 0);
  });
});
