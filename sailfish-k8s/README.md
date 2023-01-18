# Sailfish HPC K8s 

This folder contains all the kubernetes resources that is required for the Sailfish Framework.


# Configuring SailFish

To deploy your base configuration of Sailfish, modify the three files in the **overlay** folder
 - run-manager-job.yaml
 > In this file you need to add your container that will manage the Job Queue. The container is supposed to take one job and split it into multiple work items
 - runner-job.yaml 
 > These work items are picked up by the container that will be configured in this yaml.
 - kustomization.yaml
 > Finally make sure that the Internal URLS are correct with the namespace you are deploying your Sailfish to.


# Configuring your Namespace
- Make sure there is a secret called sailfish-broker-credentials-secret
Inside this secret add AMQ_USER and AMQ_PASSWORD. The values can be anything, but make sure it is a secure password.
- Since Sailfish can run distributed workloads at high scale, it must be done in a separate MachineSet. Contact the Platform team to set up a MachineSet configured for Sailfish for you.


# The Containers
After finishing the steps above, sailfish should work as intended, presuming the containers are configured to fetch the jobs and work items from the correct queue name. You can find inspiration on how to set that up in the sailfish-c# folder.