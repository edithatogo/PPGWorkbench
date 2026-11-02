# Policy currency

- [x] PC-01. Add a standard SharePoint lead review view showing source link, candidate policies, catalogue custodians, matching evidence and human disposition.
- [x] PC-02. Provide a CLI refresh with conditional writes and readback. Keep proposed relationships and unmatched or ambiguous leads explicit.
- [x] PC-03. Automatically match newly collected leads and report disposition coverage and grouped dispositions in SharePoint. Curated crosswalk expansion requires separately evidenced source identities.

- [x] PC-04. Package the scheduled cloud matcher and disposition reporting with solution references and SharePoint-hosted runtime assets. Verify the cloud run before unregistering the workstation scheduler.

- [x] PC-05. Review unmatched leads against retained notice summaries and source-reference identities; consider specific notice phrases while preserving uncertainty and human dispositions.

PC-05 native result: all 419 previously unresolved leads have evidence-scope notes. Two additional topical candidates; 11 candidates and 417 unresolved overall. No human dispositions inferred. Source-evidence cloud matcher verified with zero unchanged writes and enabled 15-minute recurrence; release 0.2.3.0. Full policy-body applicability review remains human work.

- [x] PC-06a. Deliver a bounded full-text review of accessible notices and
  identity-bound retained policy bodies. Persist supported two-sided candidate
  evidence and exact retrieval/edition gaps with conditional native readback and
  zero-change replay. Preserve existing candidates and human dispositions.
- [ ] PC-06b. Complete full coverage when publisher verification barriers,
  unavailable newsletter issues, mismatched attachments and unqualified policy
  body identities are resolved. These are explicit incomplete evidence; an
  unmatched lead does not mean no impact. Clinical applicability remains human work.

2 November: the bounded native projection and CLI are delivered. Full coverage is
incomplete for the reasons above. The scheduled cloud matcher is unchanged and
preserves curated candidates; solution version 0.2.3.0 remains applicable. Earlier
PC-05 counts are historical; current per-record outcomes and receipts stay private.

Implementation: [full-text review CLI](../../../docs/policy-currency-fulltext-review.md).
