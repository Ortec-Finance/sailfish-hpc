# Multi Cluster Sailfish Deployments
This feature connects Sailfish instances across multiple Clusters. 

## Prerequistes
- `broker-authentication` component
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
      host: sailfish-broker.rdlabs-eu.svc.cluster.local     
      secret: 
        name: broker-eu
        user-key: username
        pass-key: password
    - name: na      
      host: sailfish-broker.rdlabs-na.svc.cluster.local       
      secret: 
        name: broker-na
        user-key: username
        pass-key: password
```
The `SailfishCluster` yaml allows you to define the cluster that you wish to connect to your `sailfish-broker`. The `multi-cluster-controller` will then create Bridge Queues as a result.
You must add the `SailfishCluster` yaml in your own deployment configuration to create the bridge queus.

