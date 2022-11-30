Preparations:
- update PROJECT_ID, ADMIN_EMAIL in SET file
- If new Argolis Project, uncomment following lines inside `init.sh`
- 
```shell
gcloud resource-manager org-policies disable-enforce constraints/compute.requireOsLogin --organization=$ORGANIZATION_ID
gcloud resource-manager org-policies delete constraints/compute.vmExternalIpAccess --organization=$ORGANIZATION_ID
```

Run scripts:
```shell
./init.sh
./deploy.sh
```

login:
```shell

```