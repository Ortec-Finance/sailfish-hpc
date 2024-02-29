# Sailfish Machines
The basic configuration of Sailfish contains two components, a Run Manager and a Runner.
The Run Manager are usually light weight, as they only split the job into tasks and submit them to a queue. To prevent waiting for just one machine to spin up to handle that, we recommend that you should schedule the run manager in your Worker machinesets
However, if the Run Manager is heavy and scalable, we recommend to add a `nodeSelector` to schedule them on the sailfish machines, just like the runners


## Taints and Tolerations
Using the MachineSet Helm chart declared in `/k8s/cluster-config/machinesets` you will get three machinesets, one in each zone.

All these Sailfish Machines are by default Tainted with this:
```
- effect: NoSchedule
  key: application
  value: sailfish-hpc
```
To have your Runners schedule here, they are by default tolerating this taint by declaring this under `/spec/jobTargetRef/template/spec`:
```
tolerations:  
    - effect: NoSchedule
    key: application
    value: sailfish-hpc
```
You'd need to make a kustomize `add` operation with the same toleration if you wish to schedule the run-manager in Sailfish Machines.

In addition to the tolerations, you also need to point the workloads to land on these Nodes with the NodeSelector

## NodeSelector Label
All Sailfish Machines have this label:
```
metadata:
  labels:
    sailfish/application: {{ .Values.application }}
```
By default the Runners also implement this label in `spec/jobTargetRef/template/spec`:
```
nodeSelector:   
  sailfish/application: sailfish 
```
Similarly you'd need to make a kustomize `add` operation on the run-manager to schedule it on Sailfish Machines.

If you add the `tolerations` without adding the nodeSelector, you will risk running your workload on any Sailfish instance that is present in your cluster!

## Other workloads
In this documentation we've only mentioned scheduling the Run Manager to the Sailfish Machines, but goes with any additional workload that you wish to schedule on the Sailfish Machines.