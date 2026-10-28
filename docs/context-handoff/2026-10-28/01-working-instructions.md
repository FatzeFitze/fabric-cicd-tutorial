# Working instructions

## Purpose and collaboration

Build tutorial resources for the DNA Fabric Days two-day Fabric DataOps/CI/CD workshop. The immediate priority is adapting the completed learning series into a tested, teachable workshop; continuing Section 4 is deferred.

The organizer explicitly welcomes substantial scoping now to reduce emergency pivots later. Keep responsibilities and controls proportionate to real teams, often one or two developers. Explain why a control exists and what observable result demonstrates it.

Persist useful decisions, experiments, limitations and current state in Markdown under version control. Future chats must be able to resume without cross-project memory. Read the repository README, AGENTS.md and decision register before substantive changes.

## Evidence and decision discipline

- Label accepted organizer decisions, proposals, documentation claims and observed results separately.
- A proposal does not become accepted because implementation used it.
- Preserve the supplied Working Version 1 obligations. Use MS-01–MS-14 to trace coverage; do not silently weaken them to fit the lab.
- Do not describe unimplemented toolkit features or unrun cloud checks as working.
- Record experiment date, tenant/setup, source revision, tool versions, runner, authentication, steps, result and evidence.
- Recheck current official documentation when choosing implementation details. This handoff summarizes history; it does not freshly verify platform support.

## Authoring and publishing

Markdown in Git is the documentation source, with sections and one file per unit. Confluence is a publishing destination. Record the source revision of published pages and avoid independently maintained copies.

Each unit should provide objective, estimated time, prerequisites, explanation, numbered actions, expected observable result, troubleshooting and a checkpoint. Reference relevant minimum-standard control IDs and disclose sandbox simplifications. Use the four state types repeatedly: code, deployment, environment and runtime.

The original `TUTORIAL_AUTHORING_GUIDE.md` exists in the learning project's sources according to prior chat, but its full contents were unavailable during this export. These instructions are recovered from the workshop repository; they are not a verbatim replacement for that guide.

## Implementation direction

- Azure DevOps/Azure Pipelines is the delivery target even while Git is hosted on GitHub.
- Start with a thin reusable layer around supported Fabric tooling. Review the existing implementation before redesigning it.
- Separate sample business logic, reusable deployment components and environment configuration.
- Prove the selected cross-workspace relationships before designing a generalized manifest/framework.
- Validate and deploy one selected source snapshot across release stages; do not reread a moving branch as the release source.
- Serialize competing operations on a target and retain useful release evidence.
- Source rollback does not restore runtime data or external side effects.

## Repository boundaries

The organizer preparation repository is separate from learner solution repositories. Active preparation checkout: `C:\Users\matth\sw_dev\git_repos\fabric-cicd-tutorial`; remote: `https://github.com/FatzeFitze/fabric-cicd-tutorial`.

Documentation records initial publication to `main` and relocation outside OneDrive on 28 October 2026. Remote visibility and current branch status were not rechecked for this export.

Keep reusable code independent of company names, credentials and restricted configuration. A private GitHub repository does not establish permission to transfer company material. Community license and publication policy remain undecided. Git history transfers to Azure Repos; service connections, permissions, approvals, agents, branch policies and pipeline registrations need destination setup.
