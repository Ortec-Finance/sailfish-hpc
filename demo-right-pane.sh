#!/bin/bash
clear

. demo-magic.sh

# hide the evidence
clear

pe "oc get nodes -n openshift-machine-api --watch | grep sailfish"

pe "clear"

pe "oc get jobs -n rh-summit-demo --watch"

pe "clear"