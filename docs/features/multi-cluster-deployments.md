# Multi Cluster Sailfish Deployments
This feature connects Sailfish instances across multiple Clusters. 

## Prerequistes
- Not use `broker-authentication` component
- Not use `ephemeral-broker` component
- Not use `broker-scale-to-zero` component

## Using SailfishCluster CRD
When enabling the `multi-cluster-controller` you deploy a Controller that listens to this yaml below:

```yaml
apiVersion: ortec-finance.com/v1alpha1
kind: SailfishCluster
metadata:
  name: sailfish-cluster
spec:
  clusters:      
    - name: eu      
      host: sailfish-broker-bridge-0-svc.your-namespace.svc.cluster.local     
    - name: na      
      host: sailfish-broker-bridge-0-svc.your-namespace.svc.cluster.local   
```
The `SailfishCluster` yaml allows you to define the cluster that you wish to connect to your `sailfish-broker`. The `multi-cluster-controller` will then create Bridge Queues as a result.
You must add the `SailfishCluster` yaml in your own deployment configuration to create the bridge queus.

## Determining the Host
Every `sailfish-broker` has a bridge connector. You must reference the bridge connector of the remote sailfish instance that you'd like to connect to.

## Changes to the Gateway
The default Queue flow looks like this:
`Gateway -> sailfishJob Queue -> sailfishTask Queue`
With Multi cluster deployments, we're adding another queue inbetween the Gateway and the Job. What that means for you is that you must reference the `sailfishDispatch` Queue. There will be a shared ScaledJob spun up to handle the messages from this queue, and dispatch them based on metrics (TODO) to either the local `sailfishJob` queue or one of the remote sailfishJob Queues. 

This will result in this flow:
`Gateway -> sailfishDispatcher -> sailfishJob Queue || sailfishJob Remote Queue -> sailfishTask Queue`

## Limitations
- It is currently not possible to override the remote queue to a different name, please create a RFC this if it is required for your use case.
- It is currently not possible to reschedule ongoing Jobs, All Jobs go through the sailfish
- It is currently not possible to use the `multi-cluster-deployments` feature with the `broker-scale-to-zero`. This is due to the broker needing to be online to sustain the bridge
- It is currently not possible to schedule jobs outside of your cluster, this needs the implementation of a RedHat AMQ Interconnect 