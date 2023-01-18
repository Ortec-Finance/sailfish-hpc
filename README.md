# Introduction 
This is a HPC Framework built by Ortec Finance that works natively on kubernetes.

Sailfish uses two RedHat supported operators to function: an AMQ Broker to capture the jobs and work items, and KEDA, an autoscaler that listens to these queues and matches the amount of containers deployed to process the jobs and work items.

This enables Sailfish to complete distributed computations on container level, leveraging the Public Cloud providers flexbility on provisioning Virtual Machines.  

# Getting Started
To get started, head over to sailfish-k8s README and start with configuring your Sailfish instance
After that, you must modify your code base to listen to the AMQ Brokers message queues, to find inspiration on how to do so, checkout the sailfish-c# folder.

# Build and Test
You may simply `oc apply` to your solutions namespaces on the ORCA Cluster to deploy Sailfish, also follow the Prerequiste paragraph in the sailfish-k8s readme to setup your namespace with the proper configuration for the Operators to work.

Make sure to push the Run manager and Runner Images to the Image Registry! Changes to the image will be picked up immediately with newly created Jobs.

# Contribute
TODO