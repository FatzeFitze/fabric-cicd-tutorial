# Get ready for DNA Fabric Days

At the hackathon, you'll build a small sales solution in Microsoft Fabric, then use Git and Azure DevOps to review, test and release changes.

## What you'll get

You’ll most likely work in pairs, with the option to work solo. Each pair or solo participant will get an Azure DevOps project with three Git repositories and nine Fabric workspaces.

| Area | Azure Repos | Fabric workspaces |
| --- | --- | --- |
| Code | Code repository | Code Dev, Code Test, Code Prod |
| Data | Data repository | Data Dev, Data Test, Data Prod |
| Reporting | Reporting repository | Reporting Dev, Reporting Test, Reporting Prod |

Prod is simulated for the event. We'll also provide the Azure managed identities used by release automation. Depending on the final setup, those identities may be shared or assigned to your pair or solo setup.

## Before the event

- [ ] **Request the AD group `2307_HPM_DNA_FABRIC_DAYS_DEVOPS_CONTRIBUTOR` via IDM before the event.** Check that the request has been approved and your membership is active.
- [ ] **Install Git locally.** Open a terminal on the laptop you'll bring and run `git --version`. You should see a version number.
- [ ] **Have an IDE ready.** We recommend Visual Studio Code with its built-in Git support enabled. Any IDE you're comfortable using for local files is fine. You can run Git from a terminal if you prefer.
- [ ] **Check your work-account access when you get the event links.** On the laptop you'll bring, sign in to Microsoft Fabric and Azure DevOps. Once your training resources are assigned, check that you can open your Fabric workspace and Azure Repos repository. Let the organizers know before the event if you're blocked.

The hands-on setup uses your browser, IDE and Git. Spark runs in Fabric, and the report exercises run in the browser.

## Pick a pre-read

If one of these sounds weird, start there. The technical primers are optional and each stands on its own. Please also skim the internal DataOps guide summary to see how we apply these ideas at work.

| If this sounds weird… | Read this |
| --- | --- |
| “Clone the repo, branch off `dev`, then push and open a PR.” Did someone just ask me to do four things or six? | [Git basics](git-basics.md) |
| “CI caught it, Test passed, and Prod is waiting for approval.” Why did a three-line change need all that? | [DevOps and CI/CD](why-cicd.md) |
| “The notebook writes Delta tables to the lakehouse. The semantic model reads them.” Somewhere in there is a report, right? | [Microsoft Fabric basics](fabric-basics.md) |
| “The Azure Pipeline is queued. Its agent will use a service connection.” Is the agent waiting in line too? | [Azure DevOps basics](azure-devops-basics.md) |
| “The pilot is now productive. We need to classify it.” The slide deck still says *pilot*. Does that count? | [Our Fabric DataOps guides in brief](dataops-guides.md) |
