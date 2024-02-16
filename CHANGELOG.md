# Changelog

## v0.7.0
Added ability to set the maximum amount that your machinesets are allowed to scale to.

### Breaking changes:
To upgrade to this version you must update the machineset argo app to include the parameter:

```
    helm:
      parameters:
        - name: maxMachinesPerZone
          value: '3'
```

## v0.6.0

## v0.5.0

## v0.4.0

## v0.3.0

## v0.2.0

## v0.1.0



