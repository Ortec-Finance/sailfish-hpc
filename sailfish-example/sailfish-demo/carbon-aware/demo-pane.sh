#!/bin/bash
clear

. demo-magic.sh

# hide the evidence
clear

pe "oc apply -f carbon-aware-scheduling.yaml"
pe "curl -X POST -H 'Content-Type: application/json' -d @../../sailfish-py/body-small.json https://sailfish-gateway-rdlabs-experiment-cas-eu-west.apps.e0av02db.westeurope.aroapp.io/jobs"
pe "oc apply -f combining-metrics.yaml"
pe "curl -X POST -H 'Content-Type: application/json' -d @../../sailfish-py/body-small.json https://sailfish-gateway-rdlabs-experiment-cas-eu-west.apps.e0av02db.westeurope.aroapp.io/jobs"
pe "oc apply -f time-aware.yaml"
pe "curl -X POST -H 'Content-Type: application/json' -d @../../sailfish-py/body-small.json https://sailfish-gateway-rdlabs-experiment-cas-eu-west.apps.e0av02db.westeurope.aroapp.io/jobs"