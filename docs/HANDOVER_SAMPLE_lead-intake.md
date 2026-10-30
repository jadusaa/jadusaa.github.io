# Lead intake workflow — handover runbook (sample)

**Sample document.** This is the handover a client receives at the end of a bounded workflow build.
It is based on a workflow I built and tested independently; names, endpoints and credentials are
removed. It is shared so you can judge the documentation before commissioning anything.

---

## 1. What this workflow does

Takes incoming lead submissions, validates them, prevents duplicates, routes each lead to the right
destination, and records what happened.

**Trigger:** HTTP webhook (POST, JSON body).
**Bounded scope:** one intake path, one routing rule set, one destination.
**Explicitly out of scope:** onward sales process, CRM data cleanup, reporting dashboards.

---

## 2. How a lead moves

| Stage | What happens | If it fails |
|---|---|---|
| 1. Receive | Webhook accepts the payload | Malformed or empty input is rejected with a reason — nothing is created |
| 2. Validate | Required fields checked against a schema | Invalid submissions are held and logged, not routed |
| 3. Deduplicate | A stable key is computed from the lead identity | A repeat delivery collapses onto the existing record |
| 4. Route | Decision recorded, then executed | Unknown routes go to a holding queue, never silently dropped |
| 5. Confirm | Completion receipt written with an audit entry | Missing receipt raises an alert |

The workflow is split into separate workflows for **main**, **retry**, **replay** and **monitoring**.
That separation is deliberate: a failure in the retry path cannot take down intake.

---

## 3. The three failure cases you actually care about

**Duplicate delivery.** Webhooks get delivered more than once. This workflow computes an identity key
on intake, so a second delivery of the same lead updates the existing record instead of creating a
second one. Tested: the same payload delivered twice produces one intended action.

**A connected service breaks mid-run.** If a destination returns a timeout, 429 or 503, the workflow
retries with backoff. If it still cannot complete, it writes a failure record and raises an alert —
it does not drop the lead quietly. Tested: transient failure, repeated 429, repeated 503, and
exhausted retries.

**A run fails and needs re-sending.** Failed runs can be replayed. The replay path re-executes the
work that did not complete and skips what did, so side effects are not repeated. Tested: replay after
partial completion, replay after full failure, and no repeated side effects.

---

## 4. Where to look when something is wrong

| Symptom | First place to look | Likely cause |
|---|---|---|
| Leads not arriving | Webhook receive log | Payload rejected at validation — check the rejection reason |
| Duplicate leads | Dedupe stage, key field | Identity key built from a field that changes between submissions |
| Leads arriving but not routed | Route decision log | No rule matched — check the holding queue |
| Retries running forever | Retry sub-workflow, attempt counter | Attempt ceiling not reached because the destination keeps returning retryable errors |
| Alert fired, no visible error | Monitoring workflow | Downstream failure recorded but the main path already returned success |

---

## 5. Replaying a failed run safely

1. Confirm the run is terminal — not still retrying.
2. Check the completion receipt. If it exists, the work already finished; do not replay.
3. Trigger the replay workflow with the original run reference.
4. Verify the side-effect count before and after. If it increased by more than the pending items,
   stop and inspect the dedupe key.
5. Close the incident with the receipt reference.

**Do not** re-send the original webhook payload as a shortcut. It will be treated as a new delivery
and is only safe because deduplication catches it — not because it is the right method.

---

## 6. What was tested, and what was not

**Tested:** 23 acceptance checks covering input validation, idempotency, concurrency and atomic claim,
retry with backoff, error classification, partial-failure handling, safe replay, and audit logging.
All 23 passed on n8n 1.121.3.

**Not tested, and not claimed:** production traffic volumes, multi-tenant isolation, live third-party
API behaviour, and universal recovery from every possible failure mode. The checks cover the
scenarios listed above, not an open-ended guarantee.

---

## 7. What you own at the end

- The exported workflow JSON, importable into your own n8n instance
- This runbook
- The acceptance test evidence file
- A short recorded walkthrough
- 14 days of fixes for defects in the delivered scope

Credentials are never included. You connect your own accounts at import.

---

*Sample only. Built as an independent demonstration; no client data is reproduced here.*
