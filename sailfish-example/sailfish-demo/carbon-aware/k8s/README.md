# Deploying a Grid Intensity Exporter

## Build
1. Clone the grid-intensity app from The Green Web Foundation Repository https://github.com/thegreenwebfoundation/grid-intensity-go 
2. Follow the instructions to build your own image and push it to your registry


## Deploy

1. Include the kubernetes manifests in this folder by adding it as a `Component` to your Kustomize.

Example:
```yaml
components:
 - https://github.com/Ortec-Finance/sailfish-hpc/sailfish-example/carbon-aware/k8s?timeout=120&ref=main
```

2. Add a `ClusterRoleBinding` to allow the `sailfish-operator` ServiceAccount to access the thanos-querier metrics on OpenShift.

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: your_namespace-prom-monitoring-binding
subjects:
- kind: ServiceAccount
  name: sailfish-operator
  namespace: your_namespace
roleRef:
  kind: ClusterRole
  name: cluster-monitoring-view
  apiGroup: rbac.authorization.k8s.io
```
