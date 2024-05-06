# Sailfish Machines
The basic configuration of Sailfish contains two components, a Manager and a Worker.
The Manager are usually light weight, as they only split the job into tasks and submit them to a queue. To prevent waiting for just one machine to spin up to handle that, we recommend that you should schedule the manager in your Worker machinesets
However, if the Manager is heavy and scalable, we recommend to add a `nodeSelector` to schedule them on the sailfish machines, just like the workers


## Taints and Tolerations
Using the MachineSet Helm chart declared in `/k8s/cluster-config/machinesets` you will get three machinesets, one in each zone.

All these Sailfish Machines are by default Tainted with this:
```yaml
- effect: NoSchedule
  key: application
  value: sailfish-hpc
```
To have your Workers schedule here, they are by default tolerating this taint by declaring this under `/spec/jobTargetRef/template/spec`:
```yaml
tolerations:  
    - effect: NoSchedule
    key: application
    value: sailfish-hpc
```
You'd need to make a kustomize `add` operation with the same toleration if you wish to schedule the manager in Sailfish Machines.

In addition to the tolerations, you also need to point the workloads to land on these Nodes with the NodeSelector

## NodeSelector Label
All Sailfish Machines have this label:
```yaml
metadata:
  labels:
    sailfish/application: {{ .Values.application }}
```
By default the Workers also implement this label in `spec/jobTargetRef/template/spec`:
```yaml
nodeSelector:   
  sailfish/application: sailfish 
```
Similarly you'd need to make a kustomize `add` operation on the manager to schedule it on Sailfish Machines.

If you add the `tolerations` without adding the nodeSelector, you will risk running your workload on any Sailfish instance that is present in your cluster!

## Other workloads
In this documentation we've only mentioned scheduling the  Manager to the Sailfish Machines, but goes with any additional workload that you wish to schedule on the Sailfish Machines.