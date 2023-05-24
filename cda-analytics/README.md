# Claims Data Activator - Analytics
Claims Data Activator - Analytics component hosts definitions needed to create views and dashboards in Looker.

The [cda-analytics](../cda-analytics) folder contains the following types of Lookml files:
1. **Dashboard files** (*.dashboard.lkml) are stored at the root level
2. **Views files** (*.view.lkml) are stored under the [views](./views) folder
3. **Models files** (*.model.lkml) are stored under the [models](./models) folder


You need an instance of Looker in a Google Cloud Project for running the views and dashboards from this repository.
You can create a Looker instance by folloiwng the steps documented [here.](https://cloud.google.com/looker/docs/looker-core-instance-create#console).
Additionally, refer to the documentation [here](https://github.com/hcls-solutions/claims-data-activator/tree/main/cda-analytics/looker_terraform_deployment_script)
to configure your Looker instance.

First, you need to connect your Looker instance to the BigQuery Dataset and then you can import the lookml files into your instance to explore the dashboards.
The lookml files may need minor changes depending on the name of your BigQuery connection configuration.
