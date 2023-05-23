#!/bin/bash
clear

. demo-magic.sh
# hide the evidence
clear

pe "oc get machines -n openshift-machine-api --watch | grep sailfish"
NO_WAIT=true

pe "clear"

pe "oc get jobs -n rh-summit-demo --watch"

pe "clear"