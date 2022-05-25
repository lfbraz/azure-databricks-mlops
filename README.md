# MLOps - Azure Databricks - Batch + Online

In this repo we demonstrate how to create a simple MLOps Pipeline using Azure Databricks + Azure DevOps to automate the deployment of a ML Model from a dev to a production environment.

Please fork this repo to your own Github so you can make adjustments and customizations.

We automate the following steps:

1. Train a ML Model in a Build pipeline stage using an [MLFlow](https://mlflow.org/) experiment to track the runnings
2. Register the Model in DEV/QA Workspace
3. Transit the Model to Staging stage
4. Deploy the Model to Production (Download the artifacts and Log them to a production Workspace)
5. Transit the Model to Production stage in DEV/QA Workspace
6. Register the Model in Production Workspace
7. Create and Run a Batch Scoring Job in Production (Persisting the predictions to a Delta Table)
8. TODO: Enable MLFlow Serving

![](/images/mlops-flow.png)

# Prerequisites

The following prerequisites must be completed before you start:

* You must have a Pay-As-You-Go Azure account with administrator - or contributor-level access to your subscription. If you don't have an account, you can sign up for an account following the instructions here: https://azure.microsoft.com/en-au/pricing/purchase-options/pay-as-you-go/.

    <br>**IMPORTANT**: Azure free subscriptions have quota restrictions that prevent the workshop resources from being create successfully. Please use a Pay-As-You-Go subscription instead.

    <br>**IMPORTANT**: When you create the lab resources in your own subscription you are responsible for the charges related to the use of the services provisioned. For more information about the list of services and tips on how to save money when executing these labs, please visit the [Azure Cost Management Documentation](https://docs.microsoft.com/en-us/azure/cost-management-billing/cost-management-billing-overview#:~:text=%20Understand%20Azure%20Cost%20Management%20%201%20Plan,the%20Azure%20Cost%20Management%20%20Billing...%20More%20).

* You must have two different Azure Databricks environments, one for dev/qa and another for production. If you want you can add a different QA environment as well.

* Both Databricks environments must have the Git Integration configured with your repository using Azure DevOps Personal Tokens. Don't forget to provide read/write permissions to these tokens!

* You must have an Azure DevOps project created. We will add a MLOps pipeline there.
  
* To provide a more secure environment we will also use an [Azure Key Vault](https://docs.microsoft.com/en-us/azure/key-vault/general/basic-concepts) to keep the credentials and tokens safe.

* Create Databricks Personal Tokens to register in your Azure Key Vault.

* We use [Job Pools](https://docs.microsoft.com/en-us/azure/databricks/clusters/instance-pools/) to use pre warmed instances. Don't forget to create them and replace the pool ids in the jobs (.json) files.

# Quick start

- Import the [Customers' sample dataset](./dataset/Customer/) to your [DBFS](https://docs.microsoft.com/en-us/azure/databricks/data/databricks-file-system). This dataset will be used in the examples

- Create a variable group `databricks` in your Azure DevOps querying the secrets from your Azure Key Vault. The following variables should be created:

![](/images/akv-variables.png)

In `databricks-host` put your workspace URL `https://xxxx.azuredatabricks.net/` and for `databricks-token` the Personal Token generated in your Workspace. For instructions about this process take a look in this [doc](https://docs.microsoft.com/en-us/azure/databricks/administration-guide/access-control/tokens). You can use [AAD Tokens](https://docs.microsoft.com/en-us/azure/databricks/dev-tools/api/latest/aad/) as well.

Please put the correct values for each environment (Dev and Prod).

- Clone this repo in your own Workspace in the **DEV environment**:

![](/images/clone-in-your-workspace.png)

- Create a QA folder and clone this repo in the **DEV environment**:

![](/images/clone-in-QA-folder.png)

> You can use another Workspace as a QA environment. For simplicity in this repo we'll use the Dev Workspace as QA as well (in a different folder).

- Create a Prod folder and clone this repo in the **PROD environment**:

![](/images/clone-in-PROD-folder.png)

These Workspaces will be used to promote the artifacts (from the trained ML Model).

- Import the Pipeline in your Azure DevOps. On Pipelines menu > New Pipeline > Github (YAML) > Select the repository > Existing Azure Pipelines YAML file

![](/images/import-yaml.png)

With this we'll have the pipeline imported to your Azure DevOps project. It'll be triggered from any commit in your master/main branch.

> IMPORTANT: Replace the connection info with your own settings in the `resources` TAG of the .yaml pipeline

# TODO

- Make some settings dinamic
- Add Errors Handling
- Add MLFlow online serving
