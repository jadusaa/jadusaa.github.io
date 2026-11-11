# Shopify purchase tracking → GA4 + Meta CAPI

**Status: independent dev-store demonstration.** Every order referenced here is a test checkout on a
Shopify development store. There is no client, no customer data, and no claim of revenue improvement.

---

## The problem

Shopify's move to Customer Events broke purchase tracking for a lot of stores. Two things go wrong,
and both are silent.

**Duplicates.** The browser pixel and a server-side Conversions API call are two reports of the same
purchase. Meta counts them twice unless both carry the same `event_id`. Shopify's web pixel can fire
more than once for one order — a re-delivery, a reload mid-checkout, a retried POST — so "we send it
once" is an assumption, not a guarantee.

**Lost events with no way to see them.** If Meta is slow or returns a 5xx at the moment of the
checkout, a naive implementation drops the purchase. If it retries blindly, it can double-send. And
when GA4 succeeds while Meta fails, the dashboard shows traffic and the ad platform shows nothing —
with no record of which orders reached which destination.

## What was built

A Cloudflare Worker sits between the storefront and both destinations.

```
Shopify web pixel ──POST──▶ Worker /collect
                               │
                               ├─▶ D1: one row per order, keyed by idempotency_key
                               │      meta_state   ─┐ each with its own state,
                               │      meta_attempts │ attempt count, next_attempt_at
                               │      ga4_state     │ and last_error
                               │      ga4_attempts ─┘
                               │
                               ├─▶ GA4 Measurement Protocol  (purchase, client_id)
                               └─▶ Meta Conversions API      (Purchase, event_id)
                                        ▲
                        cron */2 min ───┘  resumes anything left pending
```

Six decisions carry the reliability:

1. **Idempotency at the door.** The key is derived from the order, not from the request. A duplicate
   delivery finds the existing row and returns without creating a second one.
2. **Two independent state machines.** `meta_state` and `ga4_state` advance separately, each with its
   own attempt count and backoff clock. One being permanently rejected does not touch the other.
3. **A permanent class distinct from retryable.** A deficient payload or a 4xx that will never
   succeed is marked `permanent` and stops. It does not burn attempts forever, and it raises an alert.
4. **Cron recovery, not in-request retry.** A redeploy or a crash mid-retry leaves a row `pending`
   with a `next_attempt_at`. The two-minute cron picks it up. Nothing is lost and nothing is
   re-sent that already succeeded.
5. **Consent is a state, not a drop.** Denied consent stores the row with both destinations
   `skipped`. It is visible and auditable rather than invisible.
6. **PII leaves hashed.** Email, phone and external id are SHA-256 hashed before the payload is
   built, and the identity columns are purged from the row after delivery.

## What was actually verified

Verified against the **deployed** Worker, not a local mock:

| Claim | Evidence |
|---|---|
| Real checkouts reach the receiver durably | **4 orders** recorded with a D1 row each |
| Both destinations accept | Those orders show `meta=sent` and `ga4=sent`, 1 attempt each |
| GA4 records the purchases | DebugView showed our purchase params; **exact revenue match** on both real orders |
| Duplicate delivery collapses | Repeated POST of a sent order → one row, no second send |
| Consent denied sends nothing | `CONSENT-DENIED` row: both destinations `skipped`, 0 attempts |
| Destinations are independent | Verified in both directions — one stays `sent` while the other retries |
| Cron recovery after a redeploy | Retry resumed unattended by the `*/2` trigger |
| Served pixel == source pixel | Byte-identical, 40,412 chars, sha256 `0a6f92b6…` |
| No secret on the unauthenticated surface | 0 matches across 3 endpoints |
| Permanent failure alerts | Alert rows written for `deficient_payload`, not an infinite retry loop |

## What is NOT proven — read this before believing the table above

- **Meta deduplication between the browser pixel and the server call is not proven.** Meta's
  per-event view for a *specific* order was observed through a **test-event code replay**, not the
  original production send. Those are different things and I am not going to merge them.
- **GA4 production reporting** beyond DebugView is not proven. Standard reports lag 24–48h and a
  short absence is not a defect — but "not yet observed" is not "verified".
- **Traffic-source attribution** is not proven.
- **Two Meta permanent failures are real and unresolved.** Both are
  `deficient_payload: user_data has no em/ph/external_id`, which is Meta correctly rejecting a
  Purchase with subcode `2804050`. A checkout where the buyer supplies no email or phone produces no
  usable identity. That is a genuine limitation of the data, not a bug I can paper over — closing it
  needs a fallback identity strategy (for example `fbp`/`fbc` cookies plus a server-side `external_id`)
  and a decision about whether to send an identity-poor event at all.
- **The pixel now points at the Worker endpoint**, replacing an earlier `loca.lt` tunnel that
  answered browser `fetch()` with a 511 interstitial. That repoint is why the tunnel is no longer in
  the customer path.

## Why this matters to a buyer

If you are running Shopify with a Meta and GA4 setup, the two questions worth asking are: *"can you
show me which orders reached which platform"* and *"what happens to a purchase when Meta is down at
the moment of checkout"*. This build exists to answer both with a row of evidence per order rather
than a screenshot of a dashboard.

What it does not do: it does not prove I have run this for a paying client, and it does not claim a
measured lift in reported conversions.

---

*Independent demonstration. Dev-store test orders only. No client data, credentials or private
correspondence are published here.*
