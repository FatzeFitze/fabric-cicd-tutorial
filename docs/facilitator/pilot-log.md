# Participant pilot record

The organizer will work through the tutorial as its first participant. Prepare one unit, observe its checkpoint, revise documentation/starter assets, and only then record the result as exercised. Keep historical reference results separate from this pilot.

Pre-run revision: following the organizer's topology question, Unit 1 provisions all nine code/data/reporting × Dev/Test/Prod workspaces up front. The first three-workspace draft was not exercised; this was a design correction, not participant runtime feedback. Subsequent provisioning evidence was received on 29 October; see the record below.

## Record

| Pilot | Unit | Instructions revision | Status | Evidence / feedback |
| --- | --- | --- | --- | --- |
| P01 | 1 — project and environments | Initial instructions: `64b6ac8`; provisioning feedback reviewed 29 October 2026 | Provisioning evidenced; participant verification pending | Supplied three successful create records cover nine workspaces and three Dev repo bindings on `dev`; participant Git access, feature checks, README edit and timing are outstanding. See [review](provisioning-review-2026-10-29.md). |
| P01 follow-up, 29 October | Earlier setup checks, now mapped to Unit 0 | Feedback on review/instructions through `81b279a` | Access/feature checks passed by organizer report | User answered yes to access to all nine workspaces and contribution to all three repos, accessible Dev Source control panes, empty workspaces and Deployment pipelines availability. DevOps access was added separately and works. Provisioning took about 1 minute, with no private endpoints; managed identity provisioning is planned later. |
| P01 next | 0 — observe and test the setup | New unit written after the feedback above; record its commit when reviewed | Narrative/teaching validation pending | Existing access checks need not be repeated. Inspection time and clarity of the new explanations are not yet reported. |
| P01 review, 29 October | 0 — observe and test the setup | Content reviewed at `daec9ca`; folder relocation changes links only | Parked after organizer content review | Organizer: "looks good"; park Unit 0 and move on. One folder per unit requested and adopted. No timed learner run or new execution result reported. |
| P02 preparation, 29 October | 1 — create a tiny sales solution | Participant lesson and `sample/tiny-sales/unit-01-notebook.py`; working tree, record followed revision at pilot | Local checks passed; Fabric walkthrough pending | Starter AST parses; independent SQLite joins confirm baseline 6 orders, quantity 13, 2 returns and 342.20 revenue, with 189.70 for later returns exclusion. Target guard accepts matching context and rejects six wrong/missing field cases. No Spark, Delta, picker, cross-workspace or timed learner run performed. See [pilot notes](unit-01-pilot-notes.md). |
| P02 walkthrough, 29 October | 1 — create a tiny sales solution | Unit 1 as supplied in the preceding chat turn, before picker-label correction; exact followed commit not supplied | Completed successfully by organizer report; UI wording corrected | Organizer reports "everything worked fine" in approximately 20–30 minutes including reading. Notebook picker uses **Add data items → From OneLake catalog**, rather than an Add lakehouse button. Updated Section 2 steps 5–6 and checked official examples supporting this path. Reworded lesson not separately replayed; no runtime code changed or new run requested. |
| P03 preparation, 29 October | 2 — capture the solution in Git | Authored after organizer reports publishing Unit 1; local starting commit `169a56e`. Record followed Unit 2 revision during pilot | Lesson/worksheet authored; Fabric commit/update not run | Uses existing Code/Data repos, records separate revisions, inspects actual generated source and applies one Markdown-only Git edit before runtime revalidation. No Git sync, raw definitions, baseline commit IDs or timing reported. See [pilot notes](unit-02-pilot-notes.md). |

Do not interpret a cloud action as completed simply because the unit describes it. The learner reports the actual resources, result and time. A facilitator-provisioning delay is separate from learner exercise time.

For each completed attempt, record the document revision, date, actual checkpoint outcome, confusing steps, errors/deviations, learner time, organizer setup time, changes made, and whether those changes need another run. Mark corrected-but-unretested instructions explicitly.

The participant README template can be copied from `examples/participant-bootstrap/README.md`; it is optional for Unit 0 and remains a facilitator/bootstrap resource. Private raw notes can stay in ignored `work/pilot/`; record useful generalized findings here.

## Interpretation of the first feedback

- The approximately one-minute figure is resource provisioning time, not a measured participant walkthrough time.
- Successful access checks are organizer-reported, not an independent live check by the assistant.
- Whether the tested participant identity differed from the provisioning identity is still unspecified; the separate-account credential rehearsal remains to be confirmed.
- At the Unit 0 access-feedback stage, no participant-authored README commit ID, first Fabric item sync, sample execution, cross-workspace binding, deployment or workload-identity result had been reported. The later P02 row records Unit 1 completion; Git sync, clean-target deployment and workload identity remain untested.
- Unit 0 is the participant entry point. Earlier setup Unit 1 is retained as a facilitator reference; current Unit 1 creates the sample assets and is now completed by organizer report.
