# Configuring Sailfish Queue Trigger

There are three files in this Sailfish configuration that need to have your custom input!

 - run-manager-job.yaml
 > In this file you need to add your container that will manage the Job Queue. The container is supposed to take one job and split it into multiple work items
 - runner-job.yaml 
 > These work items are picked up by the container that will be configured in this yaml.
 - kustomization.yaml
 > Finally make sure that the Internal URLS are correct with the namespace you are deploying your Sailfish to.


# Configuring your Namespace
- Make sure there is a secret called sailfish-broker-credentials-secret
Inside this secret add AMQ_USER and AMQ_PASSWORD. The values can be anything, but make sure it is a secure password. (Both the Application, Sailfish Broker and KEDA must use this secret)
- Since Sailfish can run distributed workloads at high scale, it must be done in a separate MachineSet. Contact the Platform team to set up a MachineSet configured for Sailfish for you.
