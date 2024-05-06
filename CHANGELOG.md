# Changelog

## v0.30.0
Adding an example of an exporter deployment that is able to export metrics into Prometheus from a Grid Intensity Provider.

## v0.28.0
Adding Sailfish-Dispatcher ScaledJob to the Multi Cluster Component. This ScaledJob enables you to schedule workloads on either the bridge queue or the local queue.

## v0.27.0
Fixed Operator Sync waves

## v0.25.0
Adding a Multi Cluster Controller Component. This Controller enables you to create Bridge Queues with ease using a `SailfishCluster` CRD.

## v0.24.0
Small documentation improvements and Refactored naming convention:
sailfish-manager -> previously known as 'run-manager' / 'job-manager'/ 'CUSTOM JOB' / 'run-manager-job.yaml'
sailfish-worker -> previously known as 'runner'/ 'tasks'/ 'task runner' / 'runner-job.yaml'

sailfish-managers execute jobs from the sailfishJob queue
sailfish-workers execute tasks from the sailfishTask queue

## v0.23.0
Refactored `sailfish-py` demo application to follow the Job Paradigm as described in the `docs/the-job-paradigm.md`

Described in the docs, is the prefered way to setup your ScaledJobs.

## v0.22.0

Fixed an issue with `sailfish-gateway` path of the `broker-authentication` component.

## v0.20.0
Fixed issue where Route generated from Knative Service would be constantly pruned by a Cluster-Scoped ArgoCD
Improved robustness of the SyncJob to prevent failed ScaledJobs and ScaledObjects 

## v0.19.0
Console and Authentication has been disabled by default.
To enable them, use the `broker-console` or `broker-authentication` Components. With this change you can remove all references and usage of `sailfish-broker-credentials-secret`.

The motivation for disabling Authentication is that the authentication protocol is not supported/gets blocked by s2i images.

It is recommended that you keep both components disabled. However `broker-console` can become handy for debugging/testing. 

## v0.17.0
Adding Machineset Azure Tags for Owner and Application
Starting this version you should set the `owner` parameter in your MachineSets to improve cost management in Azure.

## v0.16.0
- Fixing issues with sailfish instances missing logs
- Adding ability to use Spot Instances!

Removing application/product specific tolerations on MachineSets. By default, the Worker will always schedule on the Sailfish Machines, however the Manager schedules on any worker. More information on how this works can be found in `docs/sailfish-machines.md` as well on how to implement Spot Machines in `docs/features/spot-machinesets.md`

## v0.15.0
Adding Overlays for Demo

## v0.14.0
Added a new component that allows you to set the Sailfish Broker in High Availability
This will make your Queue Messages Zone redundant, which means if one zone goes down, the messages will be migrated to another.
Fixes to observability dashboard outofsync issues 

## v0.13.0
Removed `activeDeadlineSeconds` from base configuration as it does not comply with the Job Paradigm as we intend it. Added Documentation that explains how the Job Paradigm is used in Sailfish.

## v0.12.0
Added kustomization.yaml in `k8s/observability` so it works with kustomize remote ref

## v0.9.0
Restructured Folders

### Breaking Changes
To use this version you must change `sailfish-k8s` to `k8s` in all of your ArgoCD Apps and AppSets!

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
  - name: sailfish-manager
    newName: your-registry/your-manager-image
  - name: sailfish-worker
    newName: your-registry/your-worker-image
  - name: sailfish-gateway
    newName: your-registry/your-gateway-image
```

## v0.4.0
Fixed issue where this repo does not work with ApplicationSets due to the namespace field in the ScaledJob/ScaledObject Triggers. 

Now these fields no longer needs to be overriden, a ArgoCD Sync job is deployed to fix all the triggers.

### Breaking Changes
You must update your overlays to no longer replace namespaces of ScaledJob and ScaledObject `triggers`
You must update your ArgoCD Application that deploys sailfish with these ignores:
```
  ## There is a Sync job that automates the replacement of the namespace in the triggers
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
  - https://github.com/Ortec-Finance/rdlabs-sailfish-hpc//k8s/sailfish/components/ephemeral-broker/?timeout=120&ref=v0.2.0
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



