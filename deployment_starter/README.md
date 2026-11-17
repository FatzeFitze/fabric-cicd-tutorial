# Fabric deployment starter

The starter puts the common check and release workflow in YAML templates and the source verification, project check and Fabric calls in Python. A consuming repository supplies thin pipeline entry points, a versioned release mask, environment files and its own check module.

The first version supports the three-repository Tiny Sales topology and additional reports in the Reporting role that reference its existing semantic model. The supported binding definitions follow the observed Tiny Sales export shapes. The seeded lakehouse and notebook are still prerequisites. [Unit 12](../docs/tutorial/section-05-operate-and-reuse/unit-12-shared-deployment-starter/README.md).

## Entry points

| File | Responsibility |
| --- | --- |
| [CI template](templates/ci.yml) | Check out the candidate, validate the release plan and run the project check. Retain the result as an artifact. |
| [Release template](templates/release.yml) | In Test, require validation from the same run before accessing the release connection. In Prod, use the selected successful Test manifest and the approved Prod connection. Retain evidence from preflight or publishing. |
| [Python commands](release.py) | Check the selected sources and staged item definitions, run the project check in the validation job, and compare validation or Test evidence with the candidate at release time. |
| [Publishing](../toolkit/tiny_sales_release.py) | Resolve and apply the supported Fabric bindings, publish in dependency phases and verify existing item IDs and the resulting inventory. |

In the teaching setup, commit the starter and its required toolkit files together in the Code repository. The evidence records Git object IDs for the starter directory and the required toolkit files. An adoption that packages these files separately should pin its template and Python code together and record that version with the release.

## Project inputs

- Use the existing [release mask](../config/tiny-sales-release.yml) for source roles and repository pins, items and binding references, workspace IDs and desired Variable Library value sets. Keep the Code checkout as the selected Code revision.
- Put expected workspace display names, the UAMI label and the service connection reference in `config/environments/test.yml` or `prod.yml`. The release job uses the authorized connection for login and preflight compares names with Fabric. Prod also reads the reviewed `approvedTestRunId`.
- Declare the repositories as `data` and `reports` resources in the consuming YAML and match their names to the mask. For Prod, declare the `tested` pipeline resource and authorize only the intended Prod pipeline on its protected connection. Keep Prod approvals and resource permissions in Azure DevOps.
- Each item needs a unique graph key and a matching exported `<display name>.<type>` folder with a unique logical ID in `.platform`. The mask's `bindings` express references to other item keys. `after` can add a prerequisite in an earlier publish phase. The starter verifies that each report's actual `definition.pbir` references the staged semantic model by relative path.

## Static project check

Set `project_checks.static` to a Python module under `checks/`. Provide `run(repositories, plan)`, where the first argument maps `code`, `data` and `reports` to the exact checked-out paths and the second is the resolved release plan. Return normally on success or raise an exception with a diagnostic on failure. Read the exports and plan without changing them. Use the check for project rules, such as required measures or exports, and let the shared planner enforce the common configuration and dependency rules.

The validation job executes the module before the release job signs in to Fabric. Treat changes to the check as ordinary reviewed project code. The publish job rechecks the candidate and the starter version against the evidence. The project check runs only in the validation job.

See [Tiny Sales pipeline wrappers and check](../sample/tiny-sales/unit-12/) for a complete consuming example. Fabric runtime validation remains an explicit verification step in the lab.
