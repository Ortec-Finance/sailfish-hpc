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

2. Replace the `gridIntensityLocation`

Example:
```yaml
patches:
  - target:
      kind: ConfigMap
      name: grid-intensity-exporter
    patch: |-
      - op: replace
        path: /data/gridIntensityLocation
        value: NL
```

3. Currently the `grid-intensity-exporter` only supports one location, so you must deploy multiple of these if you have multiple remotes.

We've submitted a GitHub Issue to address this: https://github.com/thegreenwebfoundation/grid-intensity-go/issues/80