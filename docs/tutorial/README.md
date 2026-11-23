# DNA Fabric Days: participant tutorial

You'll build **Tiny Sales**, a small solution that turns synthetic orders into a Fabric report. You'll first promote a notebook and lakehouse with native Fabric Deployment pipelines (Model A), then use Git and Azure Pipelines to review, validate and release a change to simulated Prod (Model B).

## Start here

Use the [participant prep guide](pre-reads/README.md) to check access, set up your tools and pick background reading. Then start with **Unit 0** using your team's assigned Fabric workspaces and Azure DevOps project. Copy starter files into your team repositories as each unit introduces them.

Set aside **5–10 minutes per unit** to read the opening and reflect on the result. Make a prediction before an exercise, then compare it with what you see in Git, Azure DevOps or Fabric. At each review or approval, ask who makes the decision, what evidence they have and what their decision allows.

## Tutorial path

Follow **Units 0–10** in order. After the closing recap, you can publish a Tiny Sales baseline and try either of the two advanced labs. Both start from the same baseline.

| Unit | What you'll do |
| --- | --- |
| [0. Observe and test the setup](section-01-foundation/unit-00-observe-and-test-the-setup/README.md) | Check access to your team's workspaces and repositories and see how they connect. |
| [1. Create a tiny sales solution](section-01-foundation/unit-01-create-a-tiny-sales-solution/README.md) | Create a lakehouse and notebook, write six synthetic orders and verify that a second run leaves six orders. |
| [2. Capture the solution in Git](section-01-foundation/unit-02-capture-the-solution-in-git/README.md) | Commit the Fabric definitions, apply a Git change back to Dev and record the revisions you used. |
| [3. Native promotion](section-02-model-a/unit-03-native-promotion/README.md) | Promote the notebook and lakehouse to Test and simulated Prod, then verify where the notebook writes. |
| [4. Connect orchestration, configuration and reporting](section-03-team-delivery/unit-04-connect-orchestration-configuration-and-reporting/README.md) | Pass settings from a Variable Library into a pipeline and notebook, then build and verify a Dev report. |
| [5. Make a local feature change](section-03-team-delivery/unit-05-make-a-local-feature-change/README.md) | Edit the returned-order rule locally, review and complete the first PR into `dev`, then compare the merged revision with live Dev |
| [6. Turn review into a required check](section-03-team-delivery/unit-06-required-pr-validation/README.md) | Add a reusable source validator and demonstrate a required PR check blocking a defect and passing after the fix |
| [7. Configure and preview a release](section-04-release-automation/unit-07-configure-and-preview-release/README.md) | Fill the release mask, version the alternative value sets and review a read-only plan through the required PR check |
| [8. Verify the shared Dev workspaces](section-04-release-automation/unit-08-publish-shared-dev/README.md) | Use the Dev identity to verify workspace names, item IDs and exported bindings |
| [9. Publish Tiny Sales to Test](section-04-release-automation/unit-09-release-to-test/README.md) | Publish to Test with a managed identity and review what was deployed and who owns the items. |
| [10. Approve and publish Tiny Sales to Prod](section-04-release-automation/unit-10-release-to-prod/README.md) | Approve the tested snapshot, publish with the Prod managed identity and record first creation and runtime results |
| [Publish the Tiny Sales baseline](section-05-operate-and-reuse/README.md) | Reconcile the release tooling, validate in Test and publish the Code tag and release note for both advanced labs |
| [11. Diagnose and recover a failed Test release](section-05-operate-and-reuse/unit-11-recover-a-test-release/README.md) | Track deployments, diagnose a live workspace name mismatch and verify a corrected release |
| [12. Use a shared deployment starter](section-05-operate-and-reuse/unit-12-shared-deployment-starter/README.md) | Extend Tiny Sales with a report and project check, then verify the shared release path in Test |

## Workshop at a glance

| Section | Units | Outcome |
| --- | --- | --- |
| 1. Understand the setup and build the first result | 0–2: setup inspection, lakehouse/notebook, Git baseline | Working deterministic Dev result and traceable source |
| 2. Release the small solution with Model A | 3: native promotion and verification | Minimal two-role slice works in Test and simulated Prod |
| 3. Grow the solution and introduce team development | 4–6: Variable Library, orchestration/reporting, local feature, reusable CI/PR controls | Full Dev sample and a reviewed, validated source change |
| 4. Automate the Model B release | 7–10: environment/dependency configuration, shared Dev, Test, approved Prod | One selected source released with explicit target bindings and runtime evidence |
| [Closing recap](closing-recap.md) | After Unit 10 | Choose one control to take into your own project. |
| [5. Operate, recover and reuse](section-05-operate-and-reuse/README.md) | Publish the baseline, then pick Unit 11 or Unit 12 | A retrievable source version and a verified recovery or shared-starter release |

## Read more as you go

- [Logical and physical IDs in Fabric](reference/fabric-item-identities.md) explains how a definition in Git relates to items deployed in each environment.
- [Static validation for Fabric items](reference/static-fabric-validation.md) shows which checks can run in a pull request and which need evidence from Fabric.
- [Service connections, managed identities and federation](reference/release-service-connections.md) follows a pipeline sign-in and shows where to grant permissions.
- [Read and design a release manifest](reference/release-manifests.md) explains how to use a Test run's artifact in release review and recovery.
- [Deployment starter YAML](reference/deployment-starter-yaml.md) and [deployment starter Python](reference/deployment-starter-python.md) follow a Unit 12 run from the pipeline entry point to publishing.
- [Recover from source conflicts](auxiliary/aux-01-recover-from-source-conflicts/README.md) helps you preserve competing edits and decide how to reconcile them. Read it after Unit 5 or when you hit a conflict.

Look for **MS** numbers throughout the tutorial to see where an exercise demonstrates a Fabric Minimum Standard control. For your own project, use the Solution Classification Framework to select an operating model and read the matching column of the minimum standard. [DataOps guidelines](../source-guidelines/README.md).

## Pause and recap

Each unit ends with a short question about the result you just observed. At the turning points, take a little more time to look across the units.

- Trace the manual release and the full Dev solution before you start working from a local feature branch. [After Unit 4](section-03-team-delivery/unit-04-connect-orchestration-configuration-and-reporting/README.md#what-weve-built-so-far).
- Compare what source checks, preview and preflight can tell you before you deploy to Test. [After Unit 8](section-04-release-automation/unit-08-publish-shared-dev/README.md#what-you-built-and-where-it-leads).
- Follow a change through review, Test and approved Prod. Discuss where your own project would use different controls. [After Unit 10](section-04-release-automation/unit-10-release-to-prod/README.md#recap-and-discuss).
- Choose the first control you'd add to a real project. Do this after Unit 10 or return to it later when you have a project in mind. [Standalone closing recap](closing-recap.md) · [Production follow-up](reference/from-tiny-sales-to-production.md).

## Carry evidence from one unit to the next

Use the supplied records to link work you will reuse. A PR link can carry the diff and its review results. A manifest link can carry the deployed revisions, IDs and value set. Add your own notes when they explain an observation or connect a runtime result to the release.

| From | Carry forward | Where you use it |
| --- | --- | --- |
| Units 0–3 | Assigned workspaces and Git mappings, captured source and native release record | Units 4 and 5 build from the Dev baseline. Units 9 and 10 use the seeded target items and compare their IDs. |
| Units 4–6 | Dev definitions and runtime baseline, completed feature PR, notebook path and CI pipeline | Units 7 and 8 reuse the registered CI check, pinned revisions and observed dependencies. |
| Units 7–8 | Passing release preview and live Dev preflight, including the binding observations | Unit 9 compares the intended Test deployment with the Dev source relationships. |
| Units 9–10 | Test manifest, Test runtime results and Prod tooling PR | Unit 10 reviews the tested revisions for Prod. Section 5 uses the evidence to reconcile and validate a baseline. |
| Section 5 opener | Code tag, source pins and release note | Units 11 and 12 start from the same tagged source and check the team's Test setup against the evidence. |

## Get help during an exercise

Use the unit's troubleshooting guidance and completion checkpoint to locate the step that blocked you. If you need help, give your facilitator the unit and step, what you expected, what you observed and the exact error or run link. Keep credentials and other sensitive details out of shared notes.
