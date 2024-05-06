# Observability

In the `k8s/observability` folder is a Grafana Dashboard included.
If you want to integrate these Grafana dashboards you have to patch `/metadata/labels/app` with the name of your `dashboardLabelSelector` of your Grafana's configuration.

You can use inline patching in your ArgoCD Application, like such:

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: sailfish-observability
spec:
  destination:
    server: 'https://kubernetes.default.svc'
  project: sailfish
  source:
    path: k8s/observability
    repoURL: 'https://github.com/Ortec-Finance/sailfish-hpc.git'
    targetRevision: 'main'
    kustomize:
      patches:
        - target:
            version: v1alpha1
            group: integreatly.org
            kind: GrafanaDashboard
            name: sailfish-monitoring-dashboard
          patch: |-
            - op: replace
              path: /metadata/labels/app
              value: my_dashboard_label_selector
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
```
You can find more about this feature [here](https://argo-cd.readthedocs.io/en/stable/user-guide/kustomize/)

If you make any improvements to this dashboard please contribute them back to this repo!