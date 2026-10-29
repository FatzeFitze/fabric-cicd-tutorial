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

Do not interpret a cloud action as completed simply because the unit describes it. The learner reports the actual resources, result and time. A facilitator-provisioning delay is separate from learner exercise time.

For each completed attempt, record the document revision, date, actual checkpoint outcome, confusing steps, errors/deviations, learner time, organizer setup time, changes made, and whether those changes need another run. Mark corrected-but-unretested instructions explicitly.

The participant README template can be copied from `examples/participant-bootstrap/README.md`; it is optional for Unit 0 and remains a facilitator/bootstrap resource. Private raw notes can stay in ignored `work/pilot/`; record useful generalized findings here.

## Interpretation of the first feedback

- The approximately one-minute figure is resource provisioning time, not a measured participant walkthrough time.
- Successful access checks are organizer-reported, not an independent live check by the assistant.
- Whether the tested participant identity differed from the provisioning identity is still unspecified; the separate-account credential rehearsal remains to be confirmed.
- No participant-authored README commit ID, first Fabric item commit/update, sample execution, cross-workspace binding, deployment or workload-identity result was reported. Do not infer these from the access confirmations.
- Unit 0 is now the participant entry point. Earlier setup Unit 1 is retained as a facilitator reference; the next participant Unit 1 will create assets.
