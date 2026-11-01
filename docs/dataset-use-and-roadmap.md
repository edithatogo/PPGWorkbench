# Dataset use and business roadmap

Open **PPG Dataset Catalogue** and select **Used by**. Start with Product scope to see operational datasets. The list separates a dataset's role from its installation, recovery or qualification purpose.

| Role | Meaning | Example |
|---|---|---|
| Primary | Original observation, captured evidence or judgement recorded at this layer | Hospital capture record or reviewer assessment |
| Secondary | Records derived, reconciled or copied from another identified source | Facilities rows synchronised from the captured facilities response |
| Aggregate | Summary across records for a business decision | Follow-up digest preview |
| Unresolved | Evidence is insufficient to assign a role | Unbound qualification object |

ReadFlows and WriteFlows identify references in the selected solution export, including references in stopped definitions. A missing reference can indicate manual use, an installer or CLI, a dynamic file target, or an external dependency. The view describes design-time use. It cannot establish runtime success. DatasetSource identifies the source at dataset level. Individual records carry edition, capture or case provenance.

## Refresh after changing a flow or dataset

Use a fresh private solution export, extracted locally, and the directory inventory from the same site. Supply verified effective environment values where they override export defaults. Use physical IDs from provisioning and recovery receipts for the optional provenance map. Keep all inputs, manifests and receipts private.

```sh
.venv/bin/python scripts/ppg_dataset_lineage.py .local/export .local/catalogue.json .local/lineage.json --overrides .local/effective-values.json --provenance .local/provenance.json
node scripts/ppg_apply_dataset_lineage.mjs .local/adapter.mjs .local/lineage.json .local/receipt.json
```

For refresh, append the previously applied manifest as the final argument. Existing values differing from both the new and previous manifests require reconciliation. The adapter checks SharePoint item versions and reads the saved rows and view fields. Inspect unresolvedActions in the private manifest to identify the flow and action needing investigation. A change to a dynamic target requires binding evidence before assigning it to a dataset.

## Roadmap by business outcome

These are proposed increments. Each starts with a decision the team already needs to make.

| Vertical and audience | Existing data and flow to reuse | First increment and measure of value |
|---|---|---|
| Policy currency for policy owners | Source Update Leads, Catalogue, Document Relationships and source reconciliation | Create a review view linking a source change to affected policies and owners. Measure the proportion of leads triaged with a recorded disposition. |
| Review delivery for coordinators | Review Queue, role appointments, follow-up requests, digest previews and the monthly due report | Show overdue cases with the responsible role and next action. Measure overdue cases without an actionable owner. |
| Accreditation readiness for evidence leads | Evidence Versions, Standards Mappings, Requirement Assessments and the standards check | Show proposed mappings with missing or superseded evidence, grouped by scheme. Measure unresolved evidence gaps without sharing judgements between schemes. |
| Hospital context for service planners | Hospital Dataset Captures, Facilities, Current Metrics, Busyness Trends and the shared daily collector | Show capture freshness and missing facilities before presenting operational trends. Measure coverage against each response's declared total. |
| Safe change and recovery for platform maintainers | Dataset Catalogue, Used by, solution export and installation/recovery bindings | Prioritise unresolved actions in production writers, then report changed dependencies with each release. Measure unresolved production write destinations. |
| Reporting for service leadership | Existing monthly reports, status projections and verified datasets | Define the first question and owner before adding the roadmap Power BI dashboard. Measure whether the report answers that agreed question. |

### Investigate unresolved production writers

Pass `--bindings .local/bindings.json` to the lineage builder after verifying object identities with the installation's CLI. The private JSON contains the target `site`, a `folders` dictionary mapping physical list IDs to server-relative roots, and a `files` dictionary mapping file IDs to native parent list IDs. Include all candidate file parents for a conditional or configured file selection. Inspect both folders for a move and retain the connector's source and destination site checks.

Optional `productUse` maps physical dataset IDs to concise descriptions of documented native form, CLI or other use. Optional `externalActions` and `runObservations` use workflow display name and action name as keys. Each entry retains the exact connector parameters. External reads also record the source and relevant environment-variable values. A run observation records a parent dataset verified for the selected request and successful action. Keep the successful run, input identities and native lookup evidence with the private manifest. Run-specific parents remain unresolved for other requests.

The output separates resolved actions, selected-run observations and remaining unknown targets. A CLI writer belongs in BindingStatus. The flow columns are reserved for flow bindings.

For a confirmed parent library outside the product catalogue, record its physical ID and verified name in `externalDatasets`. Other missing parents stay on the unresolved action register, including a move that has only one catalogued endpoint.

### Recover a destination from fictional run history

For each unresolved lifecycle GET, use the exported workflow ID to list its existing runs. Select a successful run and a successful action under that exact workflow and run ID. Read the action's evaluated connector inputs, then look up the selected file and its parent library using the bound SharePoint client. A similar workflow name or a skipped action cannot establish a read. Retain the run/action identities, evaluated URL and native parent readback privately. Record whether the run chose a file ID or a path. An ID lookup identifies its parent at readback time if the file has since moved.

Supply these observations in the private bindings file under `fictionalRunReads`. Each observation contains `flowId`, `flow`, `action`, `run`, `runStatus`, `actionStatus`, `method`, `fileId` and `dataset`. The CLI accepts successful GETs for unresolved fictional actions and checks the parent against the catalogue or its explicit external dataset register. The manifest retains individual observations and the Used by view shows **ObservedReadFlows** for catalogued parents. **ReadFlows** continues to describe definition-level dependencies. Two different requests can choose different files and parents.

### Retiring a duplicate

Compare the trigger and complete definition with the surviving flow. Check solution dependencies, workflow callers, sharing, SharePoint commands and run history. Preserve the previous export and confirm that the surviving flow retains its identity, state and definition. After removing a duplicate, rebuild the catalogue from the new export so the retired identity disappears from both reader and writer columns.

The case-work router retains its two baseline reads for the original fictional ownership contract. The first compares the baseline identity and version before the conditional case update. The second checks them again before the flow records a successful commit. If the baseline changes during the update, the flow must withhold the commit and leave the journal available for reconciliation.
