# Configuring Sailfish Prometheus Trigger

There are two files in this Sailfish configuration that need to have your custom input!
Use this overlay as an example to setup yours! To prevent duplication, you can reference to this repo using a (kustomize remote ref)[https://github.com/kubernetes-sigs/kustomize/blob/master/examples/remoteBuild.md]

 - run-manager-job.yaml
 > In this file you need to add your container that will manage the Job Queue. The container is supposed to take one job and split it into multiple tasks
 - runner-job.yaml 
 > These tasks are picked up by the container that will be configured in this yaml.

In your `kustomization.yaml` you can define which components(features) you'd like to enable, you can use (kustomize remote ref)[https://github.com/kubernetes-sigs/kustomize/blob/master/examples/remoteBuild.md] for this as well. 

