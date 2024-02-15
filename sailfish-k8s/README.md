# Sailfish HPC K8s 
This folder contains all the kubernetes resources that is required for the Sailfish Framework.

# Cluster Configuration

## 1. Prometheus
Sailfish requires Openshift user-workload monitoring to be enabled, check out how to do that here:
https://docs.openshift.com/container-platform/4.13/monitoring/enabling-monitoring-for-user-defined-projects.html


## 2. Operators 
3 operators must be deployed for this demo to work: 
 - KEDA: Custom Metric Autoscaler 
 - AMQ: Red Hat Integration - AMQ Broker for RHEL 8 
 - KNATIVE: Red Hat OpenShift Serverless

The operator config are defined in `sailfish-k8s/cluster-config/operators`. You don't need to modify anything here, the operators will be deployed using ArgoCD in the final step.

## 3. Machines
We recommend to deploy seperate machinesets for Sailfish, we've provided an example for machinesets that are configured to work with ARO in this folder: `/sailfish-k8s/cluster-config/machinesets`. You can deploy these with an ArgoCD application defined in `sailfish-k8s/argocd/apps/machines.yaml`.
```
    helm:
      parameters:
        - name: clusterName
          value: your_cluster
        - name: application
          value: sailfish
        - name: networkResourceGroup
          value: your_aro_network_rg
        - name: clusterVnet
          value: your_aro_ocp_vnet
        - name: aroResourceGroup
          value: your_aro_rg
        - name: vmSize
          value: Standard_D16as_v5
```
Change these parameters to fit your cluster.

## 4. Deploying Sailfish
To deploy all components necessary to run sailfish, do `oc apply -k sailfish-k8s/argocd` in your ArgoCD namespace. This will deploy all prerequisites and deploy an environment called `sailfish` that runs the demo workloads.
If you want to deploy your own workloads, read the `README.md` file under `/sailfish-k8s/sailfish/overlay`

# Configuring Sailfish with your workloads
Sailfish is made to listen to a Prometheus metric. The workloads will scale down to zero when there is no traffic.

## Testing
To fire requests at the demo apps, execute this command:
`curl -X POST -H 'Content-Type: application/json' -d @sailfish-py/body-small.json https://sailfish-gateway-sailfish.apps.your_cluster.westeurope.aroapp.io/jobs`

Adjust the url to point at your cluster!

## Monitoring
You can apply the dashboard on the `/monitoring` folder to have a good overview of what's going on!