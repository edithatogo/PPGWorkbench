# Registry upload repeat deployment

On 2 November 2026, the deployment command ran twice with the same settings against the isolated workbench installation. The installation already had the working upload flow, its Registry action and four fictional editions on FICTIONAL-001. The first run added the missing list-scoped run-only grant. The second verified the saved configuration and made zero writes. This exercises upgrading and redeploying a populated installation. See the [CLI instructions](registry-upload-cli.md) for destination prerequisites and fresh installation.

| Independent fixture check | Before first run | After first run | After repeat |
| --- | --- | --- | --- |
| Files opened through the record's own **Open linked files** view | 46, 47, 48, 49 | Same four | Same four |
| Review Queue cases across the isolated queue | 1–6 | Same six | Same six |
| Original case attachments across the isolated queue | 5 | Same five | Same five |
| Registry UI edition 1 | Case 5 linked file 48 | Same case and file | Same case and file |
| Registry UI edition 2 | Case 6 linked file 49 | Same case and file | Same case and file |

The verifier read each working file and each case attachment from SharePoint and compared its file identity, version, length and SHA-256. It also compared the Registry link, the edition labels and classifications, the case identities and versions, modification timestamps, linked Registry IDs, submission keys, statuses and draft links. All three private queue-wide snapshots produced the same SHA-256, `95cc0e4ae630502357ffc5b7c5164294d52af0d10ad051f8f4d683cfdf97596b`.

The packaged preservation check scopes itself to the selected record. It found all four editions and five associated cases, including one earlier incomplete test case. The sixth case in the independent queue-wide check belongs to another record.

A separate read-only production check verified the deployed configuration with zero writes. The non-owner production submission remains open until a staff member submits an actual update from its Registry record. At that point verify the new file through the record link, its distinct review case, and the earlier edition against its pre-submission baseline.
