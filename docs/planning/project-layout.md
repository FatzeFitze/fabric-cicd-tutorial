# Project files and collaboration context

Date: 28 October 2026. This is the recommended working convention for this preparation repository. The organizer accepted the local checkout outside OneDrive; relocation was completed and verified on this date.

## Local checkout

Use one ordinary Git working copy as the project folder. Attach that repository root as a local project in the app so its files provide the shared project context. A project folder does not need to live in the app's generated Documents/Codex directory.

Suggested location outside cloud-file synchronization:

```text
C:\Users\matth\sw_dev\git_repos\fabric-cicd-tutorial
```

The organizer also proposed:

```text
C:\Users\matth\OneDrive\sw_dev\git_repos\fabric-cicd-tutorial
```

The OneDrive location was considered; the organizer selected the location outside OneDrive. To use it as the normal project, attach the selected folder through the app; writing outside the current allowed project folders requires the corresponding access. Do not confuse current project permissions with an inherent inability to use another local path.

Recommendation: keep active Git checkouts outside OneDrive. This is an engineering recommendation, not a statement that OneDrive repositories are categorically unsupported. File synchronization can copy files independently of Git's operations; Git metadata and generated environments add avoidable synchronization work. Microsoft's OneDrive troubleshooting guidance describes conflict-copy behavior for non-Office files [S20].

Use Git commits and pushes to transfer versioned work between computers, with a separate clone on each computer. If using the OneDrive location anyway, keep the working copy available offline and avoid using that same file-synchronized checkout concurrently on different computers. Offline availability alone does not solve concurrent synchronization. Git ignore rules do not control OneDrive synchronization.

Do not keep two competing editable copies after relocation. Verify the new copy, its Git state and remote, attach it as the project folder, and only then retire the old working location through a separate deliberate cleanup. The active checkout is now at the selected local development path above. App folder/project attachment remains a user-facing setup step.

## What belongs in the repository

| Material | Version in this repository? | Proposed location |
| --- | --- | --- |
| Tutorial units, pre-reads, facilitator/reference docs | Yes | `docs/` |
| Fabric sample definitions and synthetic input data | Yes | `sample/` |
| Generic components, checks and pipeline templates | Yes | `toolkit/`, `.azuredevops/pipelines/`, `examples/` |
| Scope, decisions, architecture and useful experiment results | Yes | `docs/planning/` and later focused reference pages |
| Concise instructions for agents working on this project | Yes | Root `AGENTS.md`; nested guidance only when needed |
| Portable project setup/test scripts and dependency definitions | Yes | Alongside the relevant component |
| Sanitized sample settings and dependency contracts | Yes | `config/`, `examples/`, or `.env.example` |
| Repo-specific repeatable agent workflows | Yes, once there is a stable need | Optional `.agents/skills/` |
| Shared, portable app environment actions or project defaults | Selectively | Optional `.codex/` files, reviewed individually |
| Personal model preferences and global instructions | No | User-level configuration outside the checkout |
| Credentials, authentication sessions, private keys, local secrets | No | Approved credential store/local environment; never in Git |
| Virtual environments, caches, logs, transient exports | Normally no | Ignored local paths |
| Raw chat transcripts and app session databases | Normally no | App-managed storage; record relevant decisions in project docs |
| Finished publication outputs | Selectively | Retain releases/artifacts when useful; prefer regenerating intermediate output |

The distinction is durable project knowledge versus personal or transient state. Agent guidance is useful project documentation and can be reviewed in the same commits as the code it governs. There is no need for a separate context repository for this workshop.

## Lightweight structure

The following is a target layout, not a claim that implementation directories already exist:

```text
fabric-cicd-tutorial/
  README.md
  AGENTS.md
  .gitignore
  docs/
    planning/
    tutorial/
    facilitator/
    reference/
  sample/
  toolkit/
  .azuredevops/pipelines/
  examples/
  config/
  .agents/skills/         # optional project workflows, when warranted
  .codex/                # optional selected portable project settings
  work/                  # ignored scratch work
  .venv/                 # ignored local environment
```

Keep `AGENTS.md` short: purpose, important scope boundaries, where the current decisions live, and how to verify work. Link detailed context rather than copying the entire design into the instruction file. Avoid a growing collection of overlapping plans and status documents; update the existing decision register and backlog.

OpenAI documents repository/global instruction layers [S16], project versus user configuration [S17], optional shareable local-environment actions [S18], and repository skills under `.agents/skills` [S19]. Do not blanket-ignore `.codex/` or copy the whole personal Codex home into Git: review each project's portable settings and keep authentication/session state separate.

## When another repository would help

Keep project-specific guidance here. If a genuinely reusable set of personal skills or editor settings emerges across many projects, maintain a separate dotfiles/skills repository containing only the shareable parts. If the deployment toolkit later becomes an independent community product, it can move to its own repository with its own instructions. Neither split is required for the current workshop.

## Working across chats

Use a focused chat for each outcome while keeping the same project folder: scope/design, feasibility experiment, reusable components, or a tutorial section. Before closing a substantial task, record material decisions, validation evidence, and remaining work in the appropriate files. A fresh chat should be able to reconstruct the current project position from the repository without reading every previous conversation.
