# MetricChat Helm Chart

This Helm chart deploys the **MetricChat** service on Kubernetes.

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


```bash
helm upgrade -i --create-namespace \
 -nmetricchat-1 metricchat metricchat/metricchat \
 --set postgresql.auth.username=<PG-USER> \
 --set postgresql.auth.password=<PG-PASS> \
 --set postgresql.auth.database=<PG-DB>
```

```bash
# deploy without TLS with custom hostname
helm upgrade -i --create-namespace \
 -nmetricchat-1 metricchat metricchat/metricchat \
  --set host=<HOST> \
 --set postgresql.auth.username=<PG-USER> \
 --set postgresql.auth.password=<PG-PASS> \
 --set postgresql.auth.database=<PG-DB> \
 --set ingress.tls=false
```