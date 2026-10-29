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

## Voice and depth

- Address the learner as "you". Use plain English, short explanations and step-by-step assignments.
- Assume mixed ALM experience. Explain the reason for a control and let the learner observe it; avoid unexplained jargon or long theory before any result.
- Give runnable starter code for business logic that is not the teaching objective. Require learners to read the relevant part, create the Fabric items themselves and verify outputs.
- Distinguish a Fabric Data Pipeline, native Deployment pipeline and Azure Pipeline by name.
- State the identity/environment assumptions relevant to the current task. Label training simplifications at the point they matter.
- Provide definite exercise instructions, while recording their untested status in the index/pilot log. Expected results are acceptance criteria, not claims that a cloud run occurred.

## Keep organizer material separate

Keep draft status, unresolved tenant/UI details, evidence gaps, validation gates, authorship notes, facilitator setup, recovery solutions and MS-control mapping in facilitator/planning files. The participant unit should contain no request to the organizer to test or approve our design.

Every new unit needs a facilitator record stating:

- Which claims are documentation-supported, locally checked, or observed in Fabric.
- What was actually tested and what remains to be piloted.
- Key UI/identity/configuration assumptions to confirm.
- Expected metrics, relevant MS controls and feedback needed.
- Dependencies that must be resolved before the next unit is written.

Do not translate a clean participant tone into a claim of validated behavior. Record actual checkpoint results and document/source revisions in the pilot log after the organizer reports them.
