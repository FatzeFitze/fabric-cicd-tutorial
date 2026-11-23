# Looking ahead — protecting historical data

## The morning the numbers change

It's 7:55 a.m. The overnight run is green. Finance opens the sales report and finds that last quarter's revenue has changed. The meeting starts in five minutes. Which number should they use?

Finance needs a number they can use in the meeting and a way to explain any correction later. The support owner needs to know whether the overnight run touched closed months, and someone who owns the metric needs to decide how to communicate a correction.

Reviewed changes, separate environments and release records give you a starting point. They help you establish which logic ran, where it ran and what was checked. To explain the difference and choose a safe fix, you also need to know which data the job read and wrote.

Tiny Sales rebuilt its disposable table from six synthetic orders. Your project may hold years of orders and corrections, with older inputs already gone from the source. The persisted tables, input archives and processing progress are part of the solution's **runtime state**. Git gives you a record of the logic and versioned settings. How you preserve and recover the data needs its own design. [DataOps architectural state model](../../source-guidelines/dataops-principles-and-scope.md#5-architectural-state-model).

## Protect history during a release

Suppose a release changes how returns are recognized from next month. Finance expects closed months to stay as reported. Another release might deliberately recalculate those months. Agree on the intended behavior before approving either change.

- **Before Prod**, review the tables, keys and dates the release or its next scheduled run may change. Rehearse schema changes and historical recalculations on a representative copy. Check the target connections and, where possible, enforce a write boundary with scoped permissions. Capture a comparable starting point, such as a table version and an agreed cutoff for closed months.
- **After Prod changes**, compare the before and after data for that same period. Check for missing or unexpected keys and reconcile business totals. Compare the relevant rows when the requirement is that they stay unchanged. Account for legitimate new arrivals and any approved recalculation before deciding whether to accept the result.

A rehearsal gives you evidence about the inputs and conditions it covered. Live data, concurrent jobs and later executions can expose new failure modes. Plan a tested way to recover any state the business depends on, including history that is normally left untouched. [Safe deployments](https://learn.microsoft.com/en-us/azure/well-architected/operational-excellence/safe-deployments) · [Fabric Minimum Standard](../../source-guidelines/fabric-minimum-standard.md#minimum-standard-by-operating-model).

Before signing off on a change that should affect only new orders, ask the reviewer to name the closed period they expect to preserve and the evidence they would compare after the first Prod run. A single total can stay the same even when individual rows changed. Pick a check that fits the promise you made to Finance.

## Make data recovery something you can run

Agree with the owner on **how much data loss is tolerable** (the recovery point objective, or RPO) and **how quickly service must be restored** (the recovery time objective, or RTO). Ask which data can be rebuilt from retained inputs and which history needs its own backup. Test whether rebuilding fits the deadline. Schedule and monitor backups or protected copies for the data that needs them, and protect recovery copies from ordinary production writers.

Turn the restore procedure into a script or pipeline that takes a known-good recovery point and an isolated destination. Have it restore the data, check schema, completeness and business totals, and stop if validation fails. Rehearse it and measure how long it takes. For a cutover back to Prod, agree who authorizes it, how to preserve legitimate writes since the recovery point, and how to validate dependent reports before reopening them. Reapplying the previous definitions and settings is a separate step when the release itself needs to be reversed.

Fabric Delta table history can help recover from some recent changes. It depends on retention of the transaction log and data files. Use a separately protected recovery copy or retained inputs if you need to recover from a failure that removes those files or makes them inaccessible. [Fabric Delta restore and retention](https://learn.microsoft.com/en-us/fabric/data-engineering/delta-lake-restore) · [Test backup and restore](https://learn.microsoft.com/en-us/azure/well-architected/reliability/reliability-test#backup-and-restore).

## Separate environments and test at realistic scale

Use small, known datasets for fast logic checks. For performance and migration tests, generate data with production-like volume, distributions and awkward cases, such as a few customers with unusually many orders. A clean six-row example gives you an expected result. A representative dataset helps you find issues that appear only with real scale or data shape.

If a test needs actual history, use an approved, scoped copy or snapshot with sensitive fields protected as required. Control who can read it, where it is stored and when it expires. Keep Dev and Test writers on their own targets and identities. A snapshot with a recorded cutoff also makes the same test repeatable as Prod continues to change. [Representative test data](https://learn.microsoft.com/en-us/azure/well-architected/operational-excellence/testing#use-representative-test-data).

## Plan for inputs that keep arriving

With a live stream, events can arrive late, out of order or more than once, including during a deployment. A streaming **checkpoint** records how far processing got and may hold intermediate state, such as a running total. Plan how a new query version will resume or rebuild that state. For example, changing how a running total groups events can make the old state unsuitable for the new query.

Keep enough input history to cover detection, recovery and catch-up. Give Dev and Test separate outputs and checkpoints, and replay a captured stream there to test bursts, late events and duplicates. Design writes so replaying an event does not count it twice. Monitor how far processing is behind the source, and check what a replay would do to downstream alerts or other actions. [Fabric Structured Streaming reliability](https://learn.microsoft.com/en-us/fabric/data-engineering/structured-streaming-overview#reliability-and-fault-tolerance) · [Late and duplicate events](https://learn.microsoft.com/en-us/fabric/data-engineering/structured-streaming-stateful-processing).

## Put the release evidence to work

If yesterday's figure changes unexpectedly, start with what the tutorial taught you to record. Find the reviewed revision, deployed target, configuration and runtime result. Then identify the input batch or event range and the table version that fed the report. With that evidence and a rehearsed recovery path, you can work out what changed, which period was affected and how to repair it.

## Rehearse the decision before the incident

Suppose last quarter changed overnight. Identify the last known-good recovery point, the inputs you can still replay and the latest time the report can reopen. Give the release record to the person checking the deployed logic and the data comparison to the person validating the recovery. Agree who can authorize the cutover after both have checked their evidence.

[Back to the closing recap](../closing-recap.md) · [Production follow-up](from-tiny-sales-to-production.md)
