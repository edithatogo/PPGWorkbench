# Keep relationship assessment membership current

After adding catalogue identities, export the catalogue, assessment register and
relationship register through the installation's qualified CLI client. Use paged
reads from the same site and retain exact preimages privately.

```sh
.venv/bin/python scripts/ppg_relationship_membership.py .local/catalogue.json .local/assessments.json .local/relationships.json .local/membership-plan.json --membership .local/source-membership.json
```

The command prepares only missing progress rows. It preserves completed reviews,
human fields and records outside the current catalogue. Identity changes become
explicit conflicts; do not apply a conflicted plan without reconciliation.

Apply the creates through the existing qualified SharePoint batch route, at most
20 operations per batch. Verify add permission, versioning and unique assessment
keys first. Journal before sending, inspect every operation result and read back
the complete expected fields. Reconcile uncertain writes before resuming; never
blindly retry a batch. Re-export and require zero creates on unchanged replay.

New rows are **Needs relationship review**, with zero qualified sources and no
authority assertion. They require full-source and endpoint review before an
assessment can be completed. This membership reconciliation does not resolve
edition conflicts, clinical applicability or publisher-access limitations.

The membership file maps each new UID to the qualified active or retained source
classification. Catalogue presence alone is insufficient; missing membership
evidence produces a conflict. Keep the source checkpoint proving the mapping.
