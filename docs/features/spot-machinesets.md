# Spot MachineSets
To save up to 80% of your compute cost, use VMs from the Spot Market. Discounts vary over time and are typically higher outside of office hours.
Just so you know, Openshift Licenses do not come with a discount and will be charged per hour on pay-as-you-go rate
## Downsides
The Public cloud provider reserves the right to withdraw your machine with a 30s notice. This will cause all of your pods running on that Machine to be evicted.
In sailfish, that is no problem, as the message in the queue will be put back for another pod to pick up, however if your runners run for a long duration, this can result in a more significant delay.

## How to enable
In your MachineSet ArgoCD Application, simply add the parameter:

```
    helm:
      parameters:
        - name: enableSpotVM
          value: 'true'
```
This will ensure that the VM type you selected with the parameter: `vmSize` will be from the Spot Market.


