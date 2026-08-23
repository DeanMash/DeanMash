import assert from "node:assert/strict";
import { describe, it } from "node:test";
import {
  DEFAULT_FREE_TRIAL_DAYS,
  isTrialActive,
  verifyWebhookSecret,
} from "./billing";
import {
  confirmEcoCashPayment,
  registerBusiness,
  requestEcoCashPayment,
  resetStore,
} from "./store";

describe("EcoCash billing — payment confirmation required", () => {
  it("grants exactly one free trial at registration", () => {
    resetStore();
    const { business, message } = registerBusiness({
      name: "Test Shop",
      vertical: "salon",
      city: "Harare",
      ownerName: "Owner",
      ownerPhone: "+263771111111",
      facebookHandle: "@TestShop",
    });
    assert.equal(business.freeTrialUsed, true);
    assert.equal(business.subscriptionStatus, "trial");
    assert.equal(business.trialCode, "FREETRIAL");
    assert.ok(business.trialEndsAt);
    assert.ok(isTrialActive(business));
    assert.match(message, /One free trial/);
  });

  it("does not activate monthly plan until payment is confirmed", () => {
    resetStore();
    const { business } = registerBusiness({
      name: "Pay Shop",
      vertical: "restaurant",
      city: "Harare",
      ownerName: "Owner",
      ownerPhone: "+263772222222",
      facebookHandle: "@PayShop",
    });

    const { payment } = requestEcoCashPayment({
      businessSlug: business.slug,
      ecocashNumber: "0771234567",
    });
    assert.equal(payment.status, "pending");
    assert.match(payment.reference, /^GG-/);

    const again = requestEcoCashPayment({
      businessSlug: business.slug,
      ecocashNumber: "0771234567",
    });
    assert.equal(again.payment.reference, payment.reference);

    const confirmed = confirmEcoCashPayment({ reference: payment.reference });
    assert.equal(confirmed.payment.status, "confirmed");
    assert.equal(confirmed.business.subscriptionStatus, "active");
    assert.ok(confirmed.business.nextBillingAt);
    assert.equal(confirmed.business.trialEndsAt, undefined);
  });

  it("rejects duplicate confirmation gracefully", () => {
    resetStore();
    const { business } = registerBusiness({
      name: "Dup Shop",
      vertical: "clinic",
      city: "Bulawayo",
      ownerName: "Owner",
      ownerPhone: "+263773333333",
      facebookHandle: "@DupShop",
    });
    const { payment } = requestEcoCashPayment({
      businessSlug: business.slug,
      ecocashNumber: "0779999999",
    });
    confirmEcoCashPayment({ reference: payment.reference });
    const again = confirmEcoCashPayment({ reference: payment.reference });
    assert.equal(again.alreadyConfirmed, true);
  });

  it("uses default trial days when no code provided", () => {
    resetStore();
    const { business } = registerBusiness({
      name: "Days Shop",
      vertical: "pharmacy",
      city: "Harare",
      ownerName: "Owner",
      ownerPhone: "+263774444444",
      facebookHandle: "@DaysShop",
    });
    const ends = new Date(business.trialEndsAt!);
    const created = new Date(business.createdAt);
    const diffDays = Math.round(
      (ends.getTime() - created.getTime()) / (1000 * 60 * 60 * 24),
    );
    assert.equal(diffDays, DEFAULT_FREE_TRIAL_DAYS);
  });

  it("validates webhook secret", () => {
    assert.equal(
      verifyWebhookSecret("mashtech-ecocash-demo-secret"),
      true,
    );
    assert.equal(verifyWebhookSecret("wrong"), false);
  });
});
