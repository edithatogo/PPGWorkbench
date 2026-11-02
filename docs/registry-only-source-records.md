# Registry-only records in source reconciliation

Locally registered policies can coexist with the institutional workbook without
being treated as unexplained workbook additions. Keep these identities separate
from active workbook identities and explicitly retained absent workbook records.

Prepare a private versioned manifest of existing Registry records. Each entry
contains `documentUID`, the destination's native `itemId`, `printedIdentifier` and
`evidenceRef`. Verify the actual identity and retained evidence first. A title
match is insufficient, and registration does not establish policy approval.

```sh
.venv/bin/python -m scripts.ppg_registry_only templates/installation/workflows/qw3source-onlyreconciliation.json .local/registry-only.json .local/compiled-source-flow.json
```

The compiler retains the existing importer's conditional writer and concurrency.
It checks the pinned records and provenance, refuses identifier collisions, and
accounts separately for workbook and Registry-only records. Explicit reviewed
adoption into the workbook reuses the same document UID and native item identity.
Unchanged replay must not write or create another record.

The distributed template contains an empty manifest. Bind native item IDs and
evidence references for each installation; never copy another installation's
physical IDs blindly. Compilation does not deploy or enable a flow. Use the
installation's existing qualified deployment route and retain exact saved
definition, readback and replay evidence privately.

Registry-only manifests, compiled destination bindings and operational checkpoints
stay private. The reusable compiler, template and fictional tests travel with
the source package.
