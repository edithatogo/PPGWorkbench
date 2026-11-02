# Retained external-reference extraction

The offline reconciliation CLI can extract literal references for selected
publisher families from hash-verified retained policy bodies. It does not fetch
URLs, choose editions, accept applicability or complete relationship assessments.

The default remains NSQHS names and Commission URLs. To inspect the supported
publisher hosts instead, use the qualified
repository-local Python 3.15.1 external-catalogue profile:

```sh
.venv/bin/python -m scripts.ppg_external_reconciliation \
  --bundle .local/external-bundle.json --local-inputs .local/retained-sources.json \
  --source-root .local/approved-sources --capture-root .local/captures \
  --publisher-host publisher.example.org \
  --publisher-host regulator.example.org \
  --no-nsqhs-names --output-dir .local/new-reference-scope
```

Install the existing hash-locked external-catalogue dependencies in the selected
profile. Inputs follow the maintained catalogue/source contract: each source pins
its document UID, original and extraction paths and SHA256 hashes, retained
version, identity qualification and extraction/conflict state. The source root
bounds the files this invocation may read. Output is create-only and private.

Choose already-qualified publisher hosts explicitly; the example hosts above
are fictional. Host syntax validation does not establish publisher authority.
Other issuers, intranet origins,
redirect destinations and superficially similar domains are not included. HTTP
links can be retained as literal historical evidence; this authorises no request.
Malformed ports and credential-bearing URLs are excluded from retrieval leads.

Each occurrence retains its own offset, page, line, source hashes and context.
Repeated citations remain distinct occurrences. Only an exact URL assertion in
the supplied publication catalogue produces a publication candidate; multiple
assertions stay ambiguous and missing matches stay unresolved. No occurrence
establishes an edition. Hash/identity/extraction holds and identities with no
qualified retained source remain visible in the coverage ledger.

The representation inventory is a separate check of supplied captured HTML.
Neither output proves full bibliographic coverage or acquisition completeness.
Use the installation's existing guarded writer and exact source bindings for
native persistence. Preserve earlier records and protected no-retrieval decisions;
verify the selected delta once and require zero-create unchanged replay.

## PDF links omitted from body text

Some retained PDFs store publisher links in URI annotations. Inspect the verified
original with `pdfinfo -url` from the existing Poppler CLI. Retain its complete
output privately with the original SHA256. This requires no publisher request.

`pdf_uri_inspection(annotation_output, original_sha256)` converts that dump into a
hashable annotation representation. It preserves physical page numbers, repeated
URI occurrences and the raw dump hash. Unsupported/malformed URI values are
recorded separately; unsupported dump rows require reconciliation. This function
does not execute the CLI, retrieve links, review the policy body or prove an
edition. The caller must verify the original bytes and bind the dump to that file.

An explicit `decode_url_wrappers=True` also records the single encoded `url`
parameter of a supported HTTPS redirect wrapper. The original wrapper is retained;
no redirect is followed and its target remains an unverified identity pointer.

Keep the returned inspection text as a new private representation, rather than
replacing the body extraction. Bind its text path/hash, `inspectionKind` and
`annotationOutputSHA256` in the source record before passing it to
`reference_scope`. Use `include_nsqhs_names=False` for this URL-only pass and
select the already-qualified publisher hosts. Native reference data must retain
the annotation representation and raw-dump hash alongside source/offset provenance.
Missing annotations do not establish an absence of references in the policy body.
