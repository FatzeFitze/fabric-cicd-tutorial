# Closing recap — From Tiny Sales to your project

## What changes when people depend on the data?

**Application lifecycle management (ALM)** is how a team develops, releases and supports a solution over time. In Tiny Sales, you reviewed a change in Git, deployed the tested version to simulated Prod with approval, and checked the result in Fabric. You did that with synthetic orders, prepared workspaces, broad training access and manual smoke checks, the quick checks you ran to verify the deployed solution worked.

Imagine Finance needs the sales report by **8 a.m. every working day**. An upstream batch can arrive late or with missing rows. A pipeline can finish successfully and still leave Finance looking at yesterday's numbers.

| Practice | Why it matters | How teams typically do it |
| --- | --- | --- |
| **Agree on the result and name its owners** | Someone needs to decide what counts as revenue and what to do if the report is late. | Agree with Finance on metric definitions, upstream data, delivery time and acceptable delays. Name who owns the result, who maintains the solution and who responds to failures. |
| **Make changes reviewable and releases repeatable** | A change to a calculation, pipeline or environment setting can affect the report. The team needs to know exactly what went live. | Version definitions and release settings in Git, review changes through pull requests, and use a pipeline or a documented sequence to promote the tested revisions. Keep the approval, versions, target and validation results together. |
| **Prepare environments and protect access** | A routine test should leave production data alone. Limiting each person's or job's access reduces accidental changes and data exposure. | Use separate environments and document or automate how to recreate workspaces, settings and connections. Verify that the scheduled job can reach its source. Set permissions for developers, deployment, scheduled jobs and readers. Keep credentials in approved storage outside Git. |
| **Test the logic, the connections and the data** | Correct code can still fail against a real source or process the wrong batch. | Test the revenue rule in isolation with known inputs (unit test). Read a representative batch through the connector in Test (integration test) and check the result through to the report after deployment. Validate each load for missing batches, duplicate orders or stale data. |
| **Monitor the result people rely on** | A failed job and a stale report both need attention before Finance acts on the numbers. | Schedule the workload, track job failures and how current the data is, and alert the support owner with a run link and the affected data. Watch run duration and capacity where they can put the deadline at risk. |
| **Practice recovery** | A faulty release and a bad data load can require different fixes. | Keep the last known-good release and its settings available for redeployment. Decide how to restore or rerun the affected data, check for duplicate results, and verify the report before telling users it is ready again. |

Match these practices to the solution's impact, data sensitivity and recovery needs. A few focused checks and short recovery instructions can go a long way for a small internal report. A critical or sensitive workload may need independent approval, tighter access and a rehearsed recovery plan. Use the operating model for your solution to decide which controls apply. For example, the Fabric Minimum Standard calls for automated technical and runtime validation in Test and after Prod deployment for **Model B**. [Solution Classification Framework](../source-guidelines/solution-classification-framework.md) · [Fabric Minimum Standard](../source-guidelines/fabric-minimum-standard.md#minimum-standard-by-operating-model) · [Microsoft Fabric operational excellence guidance](https://learn.microsoft.com/en-us/azure/well-architected/microsoft-fabric/operational-excellence).

## The history behind the report is part of the solution

In Tiny Sales, you could rebuild the training table from six orders in the notebook. A productive solution may hold years of orders and corrections, some of which the source can no longer supply. That history is part of the solution's **runtime state**. Decide what a release may change, how you’ll verify that the rest stayed intact, and how you’ll recover if a bad write gets through. Those questions get harder with production-scale Test data and live streams. [Looking ahead — protecting historical data](reference/persisted-data-in-production.md).

## Choose one improvement for your project

Take **5 minutes** after Unit 10 to close the main tutorial, or come back when you're ready to apply it to one of your projects. You can do the exercise on your own or discuss it with a partner. If you want a refresher on how the release fits together, start with the [Unit 10 recap](section-04-release-automation/unit-10-release-to-prod/README.md#recap-and-discuss).

Use the Finance example above or choose a project you know. Name one result somebody depends on and when they need it. What would you check before authorizing a release, and how would you know the result was ready on time?

- **Before merge**, what would a small unit test check? For Tiny Sales, think of the returned-order calculation with known inputs.
- **In Test**, how would you verify the connector with the intended runtime identity and check the result all the way through to the report? Consider missing, duplicate or late orders.
- **In operation**, who would respond to stale data or a failed run, and what evidence would they need to choose a safe retry or recovery?

Start with any PR, manifest or runtime result you have. If you're still planning the project, sketch what you would want that evidence to show. Write down **one control you'd add first**, the failure it addresses, what would show it worked, and who would act on the result. Use it as a discussion point in the workshop or keep it with your project notes for when you start implementing. [Production follow-up](reference/from-tiny-sales-to-production.md).

To practice diagnosing a rejected deployment and verifying the fix, try the optional Test recovery lab. [Unit 11](section-05-operate-and-reuse/unit-11-recover-a-test-release/README.md).

[Unit 10](section-04-release-automation/unit-10-release-to-prod/README.md) · [Tutorial index](README.md)
