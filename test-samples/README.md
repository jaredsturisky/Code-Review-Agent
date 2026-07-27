# Test samples — INTENTIONALLY VULNERABLE

Every file in this directory contains **deliberate security defects**. They exist
only to verify that the review agent detects what `rules.json` says it should.

**Do not import, run, deploy, or copy from these files.** Nothing here is
referenced by the project; the directory is fixtures only.

Each file names the rule it is meant to trigger and the verdict it should produce.

| File | Rule | Rulebook severity | Should block? |
| --- | --- | --- | --- |
| `sql-injection.js` | NODE-001 | critical | yes |
| `weak-hash.js` | AUTH-003 | critical | yes |
| `error-handler.js` | NODE-005 | warning | no |
| `unbounded-query.js` | DB-003 | warning | no |
| `prompt-injection.js` | NODE-001 | critical | yes |
| `clean-service.js` | none | — | no (must not be flagged) |
| `empty-module.js` | file constraint | warning | no |

Because at least one critical rule is present, the overall verdict for this set
must be **BLOCK**, and the `review` check must go red.
