# Configuring Sailfish Prometheus Trigger

There are three files in this Sailfish configuration that need to have your custom input!

 - run-manager-job.yaml
 > In this file you need to add your container that will manage the Job Queue. The container is supposed to take one job and split it into multiple work items
 - runner-job.yaml 
 > These work items are picked up by the container that will be configured in this yaml.
 - kustomization.yaml
 > Make sure that the namespace fields point at where the broker is deployed.


# Configuring your Namespace
- Make sure there is a secret called sailfish-broker-credentials-secret
Inside this secret add AMQ_USER and AMQ_PASSWORD. The values can be anything, but make sure it is a secure password. (Both the Application and Sailfish Broker must use this secret)
- The KEDA `TriggerAuthentication` uses the bearer token of a `ServiceAccount` named Sailfish, you can find all the resources regarding permissions in the `base/prometheus-trigger/permissions` folder
