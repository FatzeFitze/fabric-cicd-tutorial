# Learning-project handover review

Reviewed and imported on 28 October 2026 from the organizer-supplied `fabric-cicd-context-handoff-2026-10-28.zip`.

Archive SHA-256: `DB97406582AA591EF2F139C7298020F59681390CBCAE03DDAF97E8FF953B3A37`.

## Import and precedence

The eleven Markdown files are preserved unchanged as a [dated context snapshot](../context-handoff/2026-10-28/README.md). They are supporting source material, not new instructions overriding the organizer's decisions, the current AGENTS.md, or the minimum standard. Future changes belong in canonical planning/reference documents, rather than rewriting the snapshot.

The three archived guideline files were compared by SHA-256 with `docs/source-guidelines/`; all are byte-for-byte identical. Keep `docs/source-guidelines/` authoritative for the current Working Version 1 baseline. The archived copies exist only to preserve the self-contained handover and its relative links.

## Useful additions to project context

| Finding | Treatment in this project |
| --- | --- |
| Earlier Sections 1–3 were reported complete; Section 3 closed on 27 October 2026 | Historical learning progress, not workshop completion. Section 4 is reported parked while workshop preparation takes priority. |
| Section 3 reportedly used fabric-cicd, WIF-backed identities and separate non-production/production deployment identities | A concrete implementation to inspect before designing replacements. Do not assume every old control is mandatory hands-on Model B scope. |
| TEST candidate and released content were correlated through Git tree hashes | Reuse the provenance/content distinction when inspecting release evidence. If different merge commits represent the same content, document the comparison; otherwise prefer the same pinned source snapshot through Test and Prod. |
| Runtime evidence included pipeline/activity results, notebook results, data assertions and environment checks | Use as a reference for meaningful workshop validation. The new sample needs its own deterministic expected outputs. |
| The protected production window included deployment, runtime validation and final evidence | Evaluate this boundary for V08/V11. The old exclusive lock/runLatest choice is an example to test, not an inherited queue policy. |
| Squash reconciliation caused an ancestry problem in the older dev/main workflow | Preserve as a branch-strategy lesson. Do not add a second long-lived branch or mandate no-fast-forward merges for the simpler workshop without a demonstrated need. |
| A harmless marker change demonstrated governed forward recovery | Candidate exercise pattern for V10; distinguish this from data rollback or destructive migration recovery. |
| DataOps Models A/B/C and g-IT Targets A/B have unrelated meanings | Use explicit labels in tutorials and diagrams. A platform-service target does not determine the solution's operating model. |
| g-IT operating splits and later source-control wording were proposals | Keep them as discussion context. Do not mark them approved or silently rewrite Working Version 1. |

Detailed historical architecture and limitations are in [learning progress and findings](../context-handoff/2026-10-28/02-learning-progress-and-findings.md). Enterprise service proposals are in [enterprise platform context](../context-handoff/2026-10-28/05-enterprise-platform-context.md).

## What is already covered

The workshop scope, A/B hands-on boundary, Model C and feature-workspace explainers, manual learner bootstrap, workspace-role separation, identity distinctions, single deployment writer, and most configuration principles agree with the current planning baseline. No competing decision register or experiment numbering is needed. Continue using D01–D15 and V01–V18.

## What the handover does not supply

Subsequent update: the organizer has now supplied the test-project source separately. See the [codebase assessment](initial-codebase-review.md). The list below describes what the handover archive itself lacked; raw run evidence and full original authoring documents remain outstanding.

- The original Section 3 repository/scripts, actual pipeline definitions, raw release evidence, or tenant configuration.
- Full source contents of `CURRENT_TUTORIAL_STATE.md`, `TUTORIAL_CURRICULUM_MAP.md`, or `TUTORIAL_AUTHORING_GUIDE.md`.
- The full original project instructions or hidden project memory.
- New proof of cross-workspace binding, report/model compatibility, private connectivity, or workshop authentication/permissions.

Accordingly, the old lab's success remains organizer-reported history. It does not pass any workshop experiment. The handover's old asset names, markers, row counts and financial totals are reference examples, not constants for the new generic toolkit.

## Next use

V01 should inspect the original code and retained evidence against these historical findings, identify hardcoded dependencies, and classify each component as reusable, adaptable or replaceable. Then prove the existing workshop vertical slice. This import supplies context for that review; it does not start implementation, expand hands-on scope to Model C, or settle remaining tooling and topology choices.
