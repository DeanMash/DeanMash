import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { decideDisposition, detectFlags, scoreIsHappy } from "./engine";

describe("GladGate review gate", () => {
  it("treats 4+ as happy when language is clean", () => {
    assert.equal(scoreIsHappy(4), true);
    assert.equal(scoreIsHappy(5), true);
    assert.equal(scoreIsHappy(3), false);
  });

  it("routes clean high scores to public", () => {
    const result = decideDisposition(5, "Great sadza, fast service");
    assert.equal(result.disposition, "routed_public");
    assert.equal(result.publicReady, true);
    assert.deepEqual(result.flags, []);
  });

  it("holds low scores private", () => {
    const result = decideDisposition(2, "Food was cold");
    assert.equal(result.disposition, "held_private");
    assert.equal(result.publicReady, false);
    assert.ok(result.flags.includes("low_score"));
  });

  it("flags complaint language even on a high score", () => {
    const flags = detectFlags(5, "Tasty but the waiter was terrible and rude");
    assert.ok(flags.includes("complaint_language"));
    const result = decideDisposition(5, "Tasty but the waiter was terrible and rude");
    assert.equal(result.disposition, "held_private");
  });

  it("flags refund threats and safety concerns", () => {
    const refund = detectFlags(1, "I want a refund or I will call a lawyer");
    assert.ok(refund.includes("refund_threat"));
    const safety = detectFlags(1, "Possible food poisoning after dinner");
    assert.ok(safety.includes("safety_concern"));
  });
});
