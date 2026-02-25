## Install with Kubernetes
---
You can install MetricChat on a Kubernetes cluster. The following deployment will deploy the MetricChat container alongside a postgres instance.

### 1. Add the Helm Repository

```bash
helm repo add metricchat https://helm.metricchat.io
helm repo update
```

### 2. Install or Upgrade the Chart

Here are a few examples of how to install or upgrade the MetricChat Helm chart:

### Deploy with a pg instance
```bash
helm upgrade -i --create-namespace \
 -nmcapp-1 mcapp metricchat/metricchat \
 --set postgresql.auth.username=<PG-USER> \
 --set postgresql.auth.password=<PG-PASS> \
 --set postgresql.auth.database=<PG-DB>
```

### Deploy without TLS and with a custom hostname
```bash
# deploy without TLS with custom hostname
helm upgrade -i --create-namespace \
 -nmcapp-1 mcapp metricchat/metricchat \
  --set host=<HOST> \
 --set postgresql.auth.username=<PG-USER> \
 --set postgresql.auth.password=<PG-PASS> \
 --set postgresql.auth.database=<PG-DB> \
 --set ingress.tls=false
``` 

### Deploy without TLS and with a custom hostname
```bash
# deploy with TLS, certs by cert manager and Googole oauth enabled 
helm upgrade -i --create-namespace \
 -nmcapp-1 mcapp metricchat/metricchat \
 --set host=<HOST> \
 --set postgresql.auth.username=<PG-USER> \
 --set postgresql.auth.password=<PG-PASS> \
 --set postgresql.auth.database=<PG-DB>
 --set config.googleOauthEnabled=true \
 --set config.googleClientId=<CLIENT_ID> \
 --set config.googleClientSecret=<CLIENT_SECRET>
``` 


### Use existing Secret
1. Make sure the namespace exists, if not create it 
```bash
   kubectl create namespace <namespace>
```
2. Create the secret with the environment variables you want to override
```yaml
apiVersion: v1
kind: Secret
metadata:
  name: <secret-name>
  namespace: <namespace>
stringData:
  postgres-password: "<postgres-password>" 
  MC_DATABASE_URL: "postgresql://<postgres-user>:<postgres-password>@<postgres-host>:5432/<postgres-database>"
  MC_BASE_URL: "<base-url>"
  MC_ENCRYPTION_KEY: "<encryption-key>"
  MC_GOOGLE_AUTH_ENABLED: "false"
  MC_GOOGLE_CLIENT_ID: "<client-id>"
  MC_GOOGLE_CLIENT_SECRET: "<client-secret>"
  MC_ALLOW_UNINVITED_SIGNUPS: "false"
  MC_ALLOW_MULTIPLE_ORGANIZATIONS: "false"
  MC_VERIFY_EMAILS: "false"
  MC_INTERCOM_ENABLED: "false"
  
  # SMTP Configuration
  MC_SMTP_HOST: "<smtp-host>"
  MC_SMTP_PORT: "<smtp-port>"
  MC_SMTP_USERNAME: "<smtp-username>"
  MC_SMTP_PASSWORD: "<smtp-password>"
  MC_SMTP_FROM_NAME: "<from-name>"
  MC_SMTP_FROM_EMAIL: "<from-email>"
  MC_SMTP_USE_TLS: "true"
  MC_SMTP_USE_SSL: "false"
  MC_SMTP_USE_CREDENTIALS: "true"
  MC_SMTP_VALIDATE_CERTS: "true"
```

**Note**: When using an existing secret, the values in the secret will override the default values from the ConfigMap. You only need to include the environment variables you want to override.

3. Deploy MetricChat Application
```bash
helm install \
  mcapp ./chart \
 -n mcapp-1 \
 --set postgresql.auth.existingSecret=existing-mcapp-secret \
 --set config.secretRef=existing-mcapp-secret
```


### Service Account annotations  
For adding a SA annotation pass the following flag during `helm install` command  
`--set serviceAccount.annotations.foo=bar` 
Otherwise, set annotations directly in values.yaml file by updating
```yaml
serviceAccount:
  ...
  annotations:
    foo: bar 
```
    
### Configure node selector 
For adding a node selector to both the MetricChat app and the PostgreSQL instance set the following flag during `helm install` 
command ` --set postgresql.primary.nodeSelector.'kubernetes\.io/hostname'=kind-control-plane` 
Otherwise, set node selector directly in values.yaml
```yaml
postgresql:
  ...
  primary:
    ...
    nodeSelector: 
      kubernetes.io/hostname: kind-control-plane
```
