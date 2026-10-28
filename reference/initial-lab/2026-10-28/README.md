# Initial Fabric CI/CD learning lab: reference source

Imported from the organizer's `fabric_cicd_test_repo_content_2026_10_28.zip` on 28 October 2026. This is historical reference code, not the workshop toolkit or a participant starting repository. See the [salvage assessment](../../../docs/planning/initial-codebase-review.md).

Contains 39 source/configuration files. Six compiled Python cache files and empty directory entries were excluded. Eight files have environment-specific values replaced with neutral examples: configured workspace/repository/identity/service-connection names, tenant/workspace IDs used by networking helpers, private IP and agent name. Fabric logical IDs and their dependency references are preserved. The local original extraction is in ignored `work/imports/initial-lab-2026-10-28/`.

[IMPORT-MANIFEST.json](IMPORT-MANIFEST.json) records the archive checksum, original and retained file checksums, and which files changed. This adjusted copy is not byte-identical to the archive.

## Execution boundaries

- Nested pipeline YAML still expects the old repository layout and external Azure DevOps configuration; it is not active workshop automation.
- Deployment scripts, including plan/preflight modes, can authenticate, fetch Git refs and call APIs. They are not offline validators.
- `helper_scripts/Allow-FabricWorkspacePublicInbound.ps1` changes networking. Keep it as reference, outside participant provisioning.
- `scripts/test_fabric_private_cicd.py` can create/update/delete a canary when write/cleanup options are enabled. It is not a unit test to collect automatically.
- The notebook overwrites synthetic tables; this is not a general production data migration or recovery procedure.
- `scripts/archive/legacy-release-automation/` remains archived, without restored independent execution/import assumptions.
- `fabric-cicd==1.2.0` is the snapshot's pin, not the selected workshop version.

## Verification

All 19 Python sources and 13 source JSON/.platform files parsed successfully. The original offline definition validator and configuration lookup passed against both original and adjusted sources. A limited credential-pattern scan found no matches. YAML was inspected as text; no YAML parser or Azure Pipelines execution validation was run. No deployment, notebook, cloud authentication, networking helper or runtime probe was executed.

The ZIP contains no Git history, release-result artifacts, semantic model or report. Historical cloud success remains based on the separate handover, not these local checks.
