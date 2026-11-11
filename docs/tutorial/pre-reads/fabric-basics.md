# Microsoft Fabric basics

**Allow about 10 minutes.**

Microsoft Fabric is a cloud analytics platform for bringing in data, transforming it, analyzing it and publishing results. It brings experiences such as Data Factory, Data Engineering, Data Warehouse and Power BI into one service. You can combine them as needed. For example, a team might ingest stock movements with Data Factory, transform them with Spark and display stock levels in Power BI. [What is Microsoft Fabric?](https://learn.microsoft.com/en-us/fabric/fundamentals/microsoft-fabric-overview).

## Workspaces, capacity and storage

| Term | What it means |
| --- | --- |
| **Workspace** | A place to organize Fabric items and collaborate on them. It has roles for access, and items can have further access controls. |
| **Item** | A resource inside a workspace, such as a lakehouse, notebook, semantic model or report. Items can reference other items. |
| **Capacity** | A pool of resources used by Fabric workloads. Multiple workspaces can share a capacity. |
| **OneLake** | Fabric's shared data lake. Fabric items such as lakehouses use it to store and organize data. |

Teams can organize workspaces by solution, environment or function. For example, one solution could keep its transformations, tables and reports in different workspaces. A notebook in one workspace may refer to a lakehouse in another. The relevant identity needs access to both where its work requires it. [Workspaces in Fabric](https://learn.microsoft.com/en-us/fabric/fundamentals/workspaces) · [OneLake overview](https://learn.microsoft.com/en-us/fabric/onelake/onelake-overview).

## Follow the data

| Item or technology | Role in an analytics solution |
| --- | --- |
| **Fabric data pipeline** | Orchestrates activities such as copying files, starting a notebook and running the next activity when the previous one succeeds. It can pass inputs to the workload. |
| **Lakehouse** | Organizes files and structured tables in OneLake. Fabric lakehouses use Delta tables, which combine data files with a transaction log that tracks table changes. A SQL analytics endpoint can query exposed tables with SQL. |
| **Notebook and Spark** | A notebook holds runnable cells and explanatory text. A Fabric notebook can use Apache Spark to read, transform and write data. PySpark is the Python interface to Spark. |
| **Variable Library** | Holds named configuration values. Value sets let a team prepare different values for environments such as Dev and Prod. |
| **Power BI semantic model** | Defines how data is presented for analysis, including relationships and measures. “Available Stock” can be defined once in the model and reused by multiple reports. Direct Lake is one way a model can work with Delta tables in OneLake. |
| **Power BI report** | Displays visuals and lets people explore data from a semantic model. |

Imagine a daily stock report. A Fabric data pipeline copies the latest stock movements into OneLake and runs a notebook. The notebook cleans the input and writes a stock table in a lakehouse. A semantic model defines the measures used by the report. When someone spots an unexpected number, they can check the report filters, the measure, the table contents and the pipeline run in turn. [Data Pipelines](https://learn.microsoft.com/en-us/fabric/data-factory/pipeline-overview) · [Lakehouses](https://learn.microsoft.com/en-us/fabric/data-engineering/lakehouse-overview) · [Notebooks](https://learn.microsoft.com/en-us/fabric/data-engineering/how-to-use-notebook) · [Variable Libraries](https://learn.microsoft.com/en-us/fabric/cicd/variable-library/variable-library-cicd) · [Direct Lake](https://learn.microsoft.com/en-us/fabric/fundamentals/direct-lake-overview).

## Follow a change to the solution

**Fabric Git integration** connects a workspace to a repository, branch and directory so you can version supported item definitions. Commit changes from the workspace to Git, or update the workspace from Git to apply committed changes. **Fabric deployment pipelines** can promote supported definitions between stages. A release can also use external automation, such as an Azure DevOps pipeline calling Fabric APIs. Support for specific items, settings and references depends on the mechanism. [Fabric Git integration](https://learn.microsoft.com/en-us/fabric/cicd/git-integration/git-integration-process) · [Fabric CI/CD overview](https://learn.microsoft.com/en-us/fabric/cicd/cicd-overview).

| When someone says “pipeline” | What they mean |
| --- | --- |
| **Fabric data pipeline** | Run or orchestrate the data workload. |
| **Fabric deployment pipeline** | Promote supported Fabric item definitions between stages. |
| **Azure DevOps pipeline** | Run CI or release steps in Azure DevOps. It can validate source or coordinate a deployment. |

A **binding** is the reference that connects one item to another. If a notebook uses a lakehouse, check which lakehouse the deployed notebook resolves in the target workspace. Some relationships can be resolved by the deployment mechanism, while others require explicit configuration. Environment settings can include the active variable value set, connections and access rights. [Logical and physical Fabric item IDs](../reference/fabric-item-identities.md).

Think of four things you can inspect separately. Git shows the versioned **source definition**. The target workspace shows the **deployed definition**. Connections, bindings, permissions and active values are **environment settings** to verify. Run logs, table contents and published numbers show **runtime results**. For a lakehouse, Git can track supported metadata, while the actual rows and files live in storage. [Lakehouse Git and deployment behavior](https://learn.microsoft.com/en-us/fabric/data-engineering/lakehouse-git-deployment-pipelines).

[Back to the pre-read guide](README.md)
