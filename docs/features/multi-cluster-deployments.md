# Multi Cluster Sailfish Deployments
This feature connects Sailfish instances across multiple Clusters. 

## Prerequistes
- Not use `broker-authentication` component
- Not use `ephemeral-broker` component
- Not use `broker-scale-to-zero` component

## Using SailfishCluster CRD
When enabling the `multi-cluster` component you deploy a Controller and a ScaledJob that listens to this yaml below:

```yaml
apiVersion: ortec-finance.com/v1alpha1
kind: SailfishCluster
metadata:
  name: sailfish-cluster
spec:
  cluster:
    queue: sailfishJob # This will define what queue the dispatcher will choose as a destination when the local cluster is the best choice
  triggers:
    operator: MIN
    variables:
      - type: prometheus
        query: grid_intensity_carbon_average{location="NL"}
        clusterRef: eu # This will reference clusters defined under /spec/clusters
      - type: prometheus
        query: grid_intensity_carbon_average{location="US-CAL-CISO"}
        clusterRef: local # This will use what is defined under /spec/cluster/queue
  clusters:      
    - name: eu  
      host: sailfish-broker-bridge-0-svc.rdlabs-experiment-cas-eu-west.svc.cluster.local
```

The `SailfishCluster` manifest allows you to define the cluster that you wish to connect to your `sailfish-broker`. The `multi-cluster-controller` will then create Bridge Queues as a result.
You must add the `SailfishCluster` manifest in your own deployment configuration to create the bridge queus.

## Changes to the Gateway
The default Queue flow looks like this:
`Gateway -> sailfishJob Queue -> sailfishTask Queue`
With Multi cluster deployments, we're adding another queue inbetween the Gateway and the Job. What that means for you is that you must reference the `sailfishDispatch` Queue. There will be a ScaledJob spun up to handle the messages from this queue, and dispatch them based on metrics to either the local `sailfishJob` queue or one of the remote sailfishJob Queues. The code for the Dispatcher ScaledJob is defined in `/operator/cluster-dispatcher`

This will result in this flow:
`Gateway -> sailfishDispatcher -> (sailfishJob Queue OR sailfishJob Remote Queue) -> sailfishTask Queue`

## Determining the Host
Every `sailfish-broker` has a bridge connector already defined. You must reference the bridge connector of the remote sailfish instance that you'd like to connect to.


## Limitations
- It is currently not possible to override the remote queue to a different name, please create a RFC this if it is required for your use case.
- It is currently not possible to reschedule ongoing Jobs, All Jobs go through the sailfish
- It is currently not possible to use the `multi-cluster-deployments` feature with the `broker-scale-to-zero`. This is due to the broker needing to be online to sustain the bridge
- It is currently not possible to schedule jobs outside of your cluster, this needs the implementation of a RedHat AMQ Interconnect