# The Job Paradigm
Sailfish uses ScaledJobs to scale compute based on an Queue.
For your workloads to comply with this paradigm we need to consider a few symptoms

---

## The Problems

### Overshoot
The ScaledJobs tends to overshoot the need of jobs, this is due to delays between a job being picked up and the AMQ Broker signaling it via its Prometheus Metrics. This can sometimes result in more instances of Runners spawning per Task. Additionally, if your workloads are configured to not terminate after the completion of one Task, it can amplify this issue

### The Nature of a Job
A Kubernetes Job, is not supposed to be terminated from the outside. It's meant to run to completion and Kubernetes respects that by never terminating it unless it is evicted. 

### Keeping Runners warm
For some workloads it can be beneficial to keep the Runners warm as the initialization can be time-consuming.

---

## The Solution
To comply with these symptoms you have to design your workloads to have a stop condition, so that they can terminate gracefully. You can do this by after each computation trigger a self-destruct timer with a short grace period of ~30s.

With this grace-period, we can have a Runner capable of picking up multiple tasks which prevents the initialization time penalty. 


### Python
TODO: Code Examples

### C#
TODO: Code Examples


