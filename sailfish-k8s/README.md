# Sailfish HPC K8s 

This folder contains all the kubernetes resources that is required for the Sailfish Framework.


# Configuring SailFish
There are two configurations of Sailfish
 - Prometheus Trigger
 In this version of Sailfish, the broker will scale down to zero when there is no traffic. This is achievable by configuring the KEDA triggers to listen to the Prometheus logs of AMQ instead of querying AMQ itself.

 - Queue Trigger
 This configuration is much lighter in yaml files and is recommended to use to just get started. KEDA is configured to listen directly to the AMQ.

Pick your flavour and proceed to reading the README.md file in the Sailfish you want to deploy!


# The Containers
After finishing the steps above, sailfish should work as intended, presuming the containers are configured to fetch the jobs and work items from the correct queue name. You can find inspiration on how to set that up in the sailfish-c# folder.