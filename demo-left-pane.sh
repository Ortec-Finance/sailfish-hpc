#!/bin/bash
clear

. demo-magic.sh

# hide the evidence
clear

pe "oc apply -k sailfish-k8s/machinesets"

pe "oc apply -k sailfish-k8s/overlay/prometheus-trigger"

pe "curl -X POST -H 'Content-Type: application/json' -d @sailfish-py/body-small.json https://sailfish-gateway-rh-summit-demo.apps.ocp.ortec-finance.com/jobs"

pe "clear"

pe "curl -X POST -H 'Content-Type: application/json' -d @sailfish-py/body-large.json https://sailfish-gateway-rh-summit-demo.apps.ocp.ortec-finance.com/jobs"
