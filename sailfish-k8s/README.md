# Sailfish HPC K8s 

This folder contains all the kubernetes resources that is required for the Sailfish Framework.


# Cluster Configuration

## Prometheus
Sailfish requires Openshift user-workload monitoring to be enabled, check out how to do that here:
https://docs.openshift.com/container-platform/4.13/monitoring/enabling-monitoring-for-user-defined-projects.html


## Operators 
3 operators must be deployed for this demo to work: 
 - KEDA: Custom Metric Autoscaler 
 - AMQ: Red Hat Integration - AMQ Broker for RHEL 8 
 - KNATIVE: Red Hat OpenShift Serverless

## Machines
We recommend to deploy seperate machinesets for Sailfish, we've provided an example for machinesets that are configured to work with ARO in this folder: `/sailfish-k8s/cluster-config/machinesets`. You can deploy these with an ArgoCD application defined in `sailfish-k8s/argocd/apps/machines.yaml`.
```
    helm:
      parameters:
        - name: clusterName
          value: 'pearl-tst-s4pgx'
        - name: networkResourceGroup
          value: rg-platform-001
        - name: clusterVnet
          value: ocp-vnet
        - name: aroResourceGroup
          value: rg-aro-prd-001
        - name: vmSize
          value: Standard_D16as_v5
```
Change these parameters to fit your cluster.


## Finally..
You can `oc apply -k sailfish-k8s/argocd` to configure all cluster settings and deploy an environment called `sailfish` that runs the the demo workloads.


# Configuring Sailfish with your workloads
Sailfish is made to listen to a Prometheus metric. The workloads will scale down to zero when there is no traffic.
