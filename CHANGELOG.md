# Changelog

## v0.8.0
Implemented GH Action that creates Releases

## v0.7.0
Added ability to set the maximum amount that your machinesets are allowed to scale to.

### Breaking Changes
To upgrade to this version you must update the machineset argo app to include the parameter:

```
    helm:
      parameters:
        - name: maxMachinesPerZone
          value: '3'
```

## v0.6.0
Fixed some Readme inconsistencies

## v0.5.0
Simplified image replacements in your overlays, now you can just reference them by name!

In your overlay you can use the kustomize `images` field like such:

```
images:
  - name: sailfish-run-manager
    newName: your-registry/your-run-manager-image
  - name: sailfish-runner
    newName: your-registry/your-runner-image
  - name: sailfish-gateway
    newName: your-registry/your-gateway-image
```




## v0.4.0
Fixed issue where this repo does not work with ApplicationSets due to the namespace field in the ScaledJob/ScaledObject Triggers. 

Now these fields no longer needs to be overriden, a ArgoCD Post-Sync job is deployed to fix all the triggers.

### Breaking Changes
You must update your overlays to no longer replace namespaces of ScaledJob and ScaledObject `triggers`
You must update your ArgoCD Application that deploys sailfish with these ignores:
```
  ## There is a Post Sync job that automates the replacement of the namespace in the triggers
    - group: keda.sh
      kind: ScaledJob
      jsonPointers:
      - /spec/triggers/0/metadata/namespace
      - /spec/triggers/1/metadata/namespace
      - /spec/triggers/2/metadata/namespace
      - /spec/triggers/3/metadata/namespace
      - /spec/triggers/4/metadata/namespace
      - /spec/triggers/5/metadata/namespace
    - group: keda.sh
      kind: ScaledObject
      jsonPointers:
      - /spec/triggers/0/metadata/namespace
      - /spec/triggers/1/metadata/namespace
      - /spec/triggers/2/metadata/namespace
      - /spec/triggers/3/metadata/namespace
      - /spec/triggers/4/metadata/namespace
      - /spec/triggers/5/metadata/namespace
```


## v0.3.0
Added Ability to Scale the Sailfish Broker to Zero when there is no traffic! 
This Version also introduces the use of kustomize Components. 

The current components are:
- **sailfish-gateway** - A Knative Service that handles the trigger of a Job/Simulation
- **AMQ Broker scaling to zero** - This requires the sailfish-gateway to be enabled
- **Ephemeral Broker** - If you wish to remove the persistence of queue

To activate one of these features, simply add it in your `kustomization.yaml` like such:

```
components:
  - https://github.com/Ortec-Finance/rd-labs-sailfish-hpc//sailfish-k8s/sailfish/components/ephemeral-broker/?timeout=120&ref=v0.2.0
```
If you intend to use the AMQ Broker scaling to zero component you must update your ArgoCD Application that deploys sailfish-hpc with these ignores:

```
  ignoreDifferences:
    - group: broker.amq.io
      kind: ActiveMQArtemis
      jsonPointers:
      - /spec/deploymentPlan/size
```

## v0.2.0
Updated Cluster Configuration to properly deploy operators
Updated Machine Configuration to support OCP 4.12 and parameterized taints and labels



