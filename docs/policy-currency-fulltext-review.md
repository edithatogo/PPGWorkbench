# Full-text policy currency review

The scheduled cloud matcher remains the first pass. A bounded CLI review can add
supported links using full source notices and retained policy bodies. A matching
word, a feed summary, a cover email, or a publisher verification page is insufficient.

Keep downloaded bytes, full text, source bindings and review selections private.
Reuse verified source hashes. Extract all PDF pages; use local OCR for image-only
or garbled text and retain its recognition limitation. Inspect attached notices
against their subject: an attachment on the correct list item may still contain
the wrong document. Do not treat unreadable correspondence or a missing full
newsletter issue as reviewed content.

Bind each policy body to its catalogue identity and captured edition. A matching
historical file does not establish current approval. Keep uncovered catalogue
identities explicit. Review the relevant passages on both sides, including product,
formulation, age group, setting and whether the notice is a proposal or historical
alert. Reject incidental word overlap and reference-list-only coincidences.

Use the repository-local Python 3.15 interpreter:

```sh
.venv/bin/python scripts/ppg_currency_fulltext_review.py \
  .local/fulltext/input.json .local/fulltext/review.json
```

The private input contains `leads`, `notices`, `policies` and `selections` arrays.
Each full body requires `text`, its UTF-8 `textSHA256`, verified `captureSHA256`,
`state: retrieved`, `fullText: true` and an exact extraction `scope`. Notices bind
`id` and `leadGUID`. Policies bind `uid`, native `id`, title, custodian and
`identityBasis`, with the retained edition limitation. An explicit selection pins
the notice text hash, policy capture hash, a passage anchor on each side and the
reason the link merits review. Changed hashes, absent passages and identity
changes fail before a packet is produced.

The packet contains candidates, not clinical applicability decisions. Preserve
human dispositions and existing candidates. Apply only reviewed projections with
exact native GUID/preimage checks and ETags, bounded SharePoint batches and
per-operation result inspection. Record retrieval blockers and full-text coverage
in `CurrencyReviewEvidence`, and capture identities in `CurrencyNoticeProvenance`.
Keep full bodies in the private evidence store. An unchanged replay should produce
zero writes; an uncertain native write requires reconciliation before another send.

The cloud matcher preserves these curated candidate records because they no
longer have the untouched generated-unresolved evidence signature. It continues
matching new arrivals and publishing disposition coverage. No cloud definition,
schedule, solution membership or new connector is needed for this review lane.

For coverage reporting, keep two separate denominators: leads with a complete
qualified source notice, and catalogue identities with a qualified full policy
body. A successful retrieval may still be a cover message, garbled extraction,
wrong attachment or incomplete issue. A lead without a selected link stays
unresolved even when its notice was read; do not turn missing evidence into a
“No impact” disposition. Keep actual counts and per-record blockers in private
receipts and the native review fields.

## Retained policy-body identities

Use the body qualifier before adding a previously unqualified body to the review
corpus. It checks the primary heading and printed document family, or an existing
native catalogue UID binding. Common labels such as “Drug infusion guideline” and
medicine names mentioned only in the body cannot replace the expected heading.
Identifier variants require capture-pinned reviewed evidence; a different document
number remains a conflict. The original register identifier is preserved.

```sh
.venv/bin/python scripts/ppg_policy_body_identity.py \
  .local/body-identities/input.json .local/body-identities/qualification.json
```

The private input contains `policies`, `documents` and explicit `bindings` arrays.
A binding supplies `uid`, `sha256` and, when applicable, `nativeUID`, `variant` or
`titleReview`. Policy and capture identities must be unique. Documents retain the
verified original-byte SHA256, full text, text SHA256 and extraction scope. A
reviewed variant pins the original expected identifier, observed identifier,
capture hash and rationale. A reviewed renamed heading pins its actual passage
and capture hash. None of these establish current approval or clinical applicability.

Some retained originals are ZIP-wrapped Word files. The qualifier's
`unpack_single_document` helper retains the container and member hashes and reads
one original without extracting arbitrary paths. Multiple-version packages remain
intact and require explicit member selection; they are never flattened silently.

`BodyIdentityState`, `BodyIdentityEvidence` and `BodyIdentityJSON` on the catalogue
record the retained bindings or exact holds. The **Policy body identities** view
exposes state and evidence; the JSON contains capture/edition/source links. These
optional fields are in the whole-product installation schema and companion release.
Source identifiers, source captures and human annotations remain authoritative in
their existing fields. A bound historical body is not proof that the register's
current edition has been located. Keep source-notice retrieval gaps separate.

Provision an existing installation with the retained qualified SharePoint adapter:

```sh
node scripts/ppg_policy_body_ledger.mjs \
  .local/adapter.mjs .local/body-identities/schema-receipt.json
```

An optional third argument binds the exact destination list ID. Existing field types
and the view are read back; conflicting definitions are held for reconciliation.
The command does not populate bindings, change register identifiers or enable flows.
