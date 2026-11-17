# Closing recap — From Tiny Sales to your project

Take **5 minutes** after Unit 10 to close the main tutorial, or come back when you're ready to apply it to one of your projects. You can do the exercise on your own or discuss it with a partner. If you want a refresher on how the release fits together, start with the [Unit 10 recap](section-04-release-automation/unit-10-release-to-prod/README.md#recap-and-discuss).

Choose a project you know, or imagine Tiny Sales now reads orders from an upstream system and Finance relies on the report every morning. Name one result somebody depends on and when they need it. What would you check before authorizing a release, and how would you know the result was ready on time?

- **Before merge**, what would a small unit test check? For Tiny Sales, think of the returned-order calculation with known inputs.
- **In Test**, how would you verify the connector with the intended runtime identity and check the result all the way through to the report? Consider missing, duplicate or late orders.
- **In operation**, who would respond to stale data or a failed run, and what evidence would they need to choose a safe retry or recovery?

Start with any PR, manifest or runtime result you have. If you're still planning the project, sketch what you would want that evidence to show. Write down **one control you'd add first**, the failure it addresses, what would show it worked, and who would act on the result. Use it as a discussion point in the workshop or keep it with your project notes for when you start implementing. [Production follow-up](reference/from-tiny-sales-to-production.md).

[Unit 10](section-04-release-automation/unit-10-release-to-prod/README.md) · [Tutorial index](README.md)
