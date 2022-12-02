Preparations:
```shell
export PROJECT_ID = <put-id-here>
export API_DOMAIN=mydomain.com
```

If you do not have domain, leave a dummy one and then on deploy step, after running terraform, set it to the external IP.

For Argolis Environments: 
```shell
gcloud config set project $PROJECT_ID
ORGANIZATION_ID=$(gcloud organizations list --format="value(name)")
gcloud resource-manager org-policies disable-enforce constraints/compute.requireOsLogin --organization=$ORGANIZATION_ID
gcloud resource-manager org-policies delete constraints/compute.vmExternalIpAccess --organization=$ORGANIZATION_ID
```

Run terraform script and prompted to approve terraform changes, do so:
```shell
./init.sh
```

When not using DNS name, Update API_DOMAIN in SET accordingly:
```shell
./init_domian_with_ip.sh
```



After that deploy:
```shell
./deploy.sh
```