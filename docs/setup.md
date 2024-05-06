# Sailfish HPC K8s 
To get started with using Sailfish there are a few steps!

To make versioning simple and to follow DRY principles, to deploy the Cluster Operators and Machines you can make an ArgoCD Application to reference the resources:
  - `k8s/cluster-config/operators`
  - `k8s/cluster-config/machinesets`

For Sailfish itself, this repository is designed around a kustomize feature called [kustomize remote ref](https://github.com/kubernetes-sigs/kustomize/blob/master/examples/remoteBuild.md).
This design makes it easy upgrade to new features of Sailfish! Read more in #2 Deploying Sailfish on how you can use that.

You can find examples of the ArgoCD Applications under `sailfish-example/argocd`.

# 1. Cluster Configuration
- Step A and B should be done once per Cluster.
- Step C is something you need to setup atleast once yourself.

## 1a Prometheus
Sailfish requires Openshift user-workload monitoring to be enabled, check out how to do that here:
https://docs.openshift.com/container-platform/4.13/monitoring/enabling-monitoring-for-user-defined-projects.html


## 1b Operators 
To deploy or synchronize your operators to work with the current sailfish version, 

3 operators must be deployed for this demo to work: 
 - KEDA: Custom Metric Autoscaler 
 - AMQ: Red Hat Integration - AMQ Broker for RHEL 8 
 - KNATIVE: Red Hat OpenShift Serverless

The operator config are defined in `k8s/cluster-config/operators`. You don't need to modify anything here!


## 1c Machines
We recommend to deploy seperate machinesets for Sailfish, we've provided an example for machinesets that are configured to work with ARO in this folder: `/k8s/cluster-config/machinesets`. You can deploy these with an ArgoCD application, find the example here: `sailfish-example/argocd/apps/machines.yaml`.
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

## 2 Deploying Sailfish

### Option 1: Sailfish Demo
After configuring the cluster, you can `oc apply -k k8s/sailfish/overlay` into a namespace. This will deploy all components and is defined by default to run the python demo in `sailfish-example/sailfish-py`. If you cannot `oc apply` you can also add the argocd configuration defined in `sailfish-example/argocd/apps/sailfish.yaml`.

#### Testing the Demo
To fire requests at the demo apps, execute this command:
`curl -X POST -H 'Content-Type: application/json' -d @sailfish-py/body-small.json https://sailfish-gateway-sailfish.apps.your_cluster.westeurope.aroapp.io/jobs`
>Adjust the url to point at your cluster!

### Option 2: Bring your own Container
While by default you will deploy the demo app using `oc apply -k k8s/sailfish/overlay`, you can also easily override the demo app with your own image and settings!
You will do this in your own repository, reference to this repo using a [kustomize remote ref](https://github.com/kubernetes-sigs/kustomize/blob/master/examples/remoteBuild.md).

1. In your own repository, in your `kustomization.yaml`, use the *kustomize remote ref* feature, add the `base/prometheus-trigger` configuration under `resources:`
2. Similarly, choose which features you'd like to enable from the components, and add those under `components:`
> Use the `k8s/sailfish/overlay` as inspiration on how you should set this up!

There are two files in this Sailfish configuration that need to have your custom input!

 - manager-job.yaml
 > In this file you need to add your container that will manage the Job Queue. The container is supposed to take one job and split it into multiple tasks
 - worker-job.yaml 
 > These tasks are picked up by the container that will be configured in this yaml.

In your `kustomization.yaml` you can define which components (features) you'd like to enable, you can use [kustomize remote ref](https://github.com/kubernetes-sigs/kustomize/blob/master/examples/remoteBuild.md) for this as well. 


# 3 Configuring your Workloads to work with Sailfish
Sailfish is made to listen to a Prometheus metric. The workloads will scale down to zero when there is no traffic.
You can use the C# or Python examples under `sailfish-example` to send messages to the AMQ Broker.

## Monitoring
You can apply the dashboard on the `/monitoring` folder to have a good overview of what's going on!