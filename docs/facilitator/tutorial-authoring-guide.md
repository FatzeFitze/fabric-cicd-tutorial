# Participant tutorial authoring guide

Working convention, 29 October 2026. The organizer asked for participant-ready Markdown from the first draft, with organizer checks outside the lessons. Apply this convention to Unit 1 onward; Unit 0 remains parked as reviewed.

## Standard lesson structure

1. **Title, estimated time and created/changed resources.** Describe the observable result in a sentence.
2. **What you will learn.** Use a short list of concrete abilities.
3. **Before you begin.** Link the preceding unit and required resources; identify access, tools and starting state. Do not make the learner read our planning documents to start.
4. **Understand what you are building.** Explain concepts needed now, with a small diagram when useful. Separate delivery flow from data flow.
5. **Numbered assignments.** Use imperative steps, exact item names and clear workspace/environment selection. Explain important choices next to the action. End each assignment with an expected result.
6. **Troubleshooting.** Give specific symptoms and bounded checks. Do not invent alternate architectures to work around an unverified path.
7. **Completion checkpoint.** Use observable outcomes, a short reflection and the state to retain for the next unit. Ask learners to retain item links/time/error details; keep private identifiers out of published answers.
8. **References and navigation.** Link relevant official pages near claims and in a compact reference list. Link only to future units that actually exist.

Use ordinary Markdown headings, relative repository links, portable tables and Mermaid where appropriate. Each unit lives in its own folder with a `README.md`; resources used only by that lesson may live beside it. Reusable sample code, fixtures, toolkit and pipelines have canonical locations outside the unit. Avoid copying their implementation into multiple lessons. Code may be inline when the lesson is its single authoritative source.

Create the unit folder and README entry point immediately, even during preparation/rehearsal. Link the canonical rehearsal and shared resources from there, label their validation status in the index, and publish the files with the authorized repository workflow. The organizer reads/tests on a work PC via GitHub; a chat-only link or a file hidden solely among facilitator material is insufficient navigation. A preparation entry point does not make a unit finalized or validated.

## Voice and depth

- Address the learner as "you". Use plain English, short explanations and step-by-step assignments.
- Assume mixed ALM experience. Explain the reason for a control and let the learner observe it; avoid unexplained jargon or long theory before any result.
- Explain unfamiliar Fabric responsibilities at the point of use, especially workspace/item identities, resource linkage and environment bindings that may have been hidden by a centrally managed on-premises setup. Give the location, purpose, alternatives and observable check for a setting; a click path alone is insufficient. Do not assume every on-premises platform lacked such controls.
- Give runnable starter code for business logic that is not the teaching objective. Require learners to read the relevant part, create the Fabric items themselves and verify outputs.
- Use the UI's actual field names and distinguish conceptual mappings from visible input fields. Explain generated runtime content separately from authored source. For web editors, state whether edits autosave instead of assuming a Save button exists.
- Distinguish a Fabric Data Pipeline, native Deployment pipeline and Azure Pipeline by name.
- State the identity/environment assumptions relevant to the current task. Label training simplifications at the point they matter.
- Keep creator, visible item owner, associated/default identity, deployment caller, runtime executor and connection/data-access identity distinct where relevant. Test first creation separately from updating an existing item; do not generalize one ownership result to every Fabric item/API.
- Provide definite exercise instructions, while recording their untested status in the index/pilot log. Expected results are acceptance criteria, not claims that a cloud run occurred.
- Use optional pages under `docs/tutorial/reference/` for topics that benefit from tradeoffs, examples or discussion prompts. Link them at the point of use and from the tutorial index. Keep task instructions and checkpoints in the lesson, with exercise-specific worksheets beside it.
- Give learners short, descriptive commit messages for the Git changes they make. For a PR exercise, supply a title and a brief description with **Change** and **Validation**. Ask learners to replace expected outcomes with observed results and links before completing the PR.

## Keep organizer material separate

Write the current exercise path for participants. Share temporary workarounds, migration steps between draft revisions and directions for the organizer in chat. Use facilitator notes for durable pilot evidence and setup guidance.

Keep draft status, unresolved tenant/UI details, evidence gaps, validation gates, authorship notes, facilitator setup, recovery solutions and MS-control mapping in facilitator/planning files. The participant unit should contain no request to the organizer to test or approve our design.

Every new unit needs a facilitator record stating:

- Which claims are documentation-supported, locally checked, or observed in Fabric.
- What was actually tested and what remains to be piloted.
- Key UI/identity/configuration assumptions to confirm.
- Expected metrics, relevant MS controls and feedback needed.
- Dependencies that must be resolved before the next unit is written.

Do not translate a clean participant tone into a claim of validated behavior. Record actual checkpoint results and document/source revisions in the pilot log after the organizer reports them.
