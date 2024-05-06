### THIS IS A PLACEHOLDER FOR THE CARBON AWARE DEMO
#!/bin/bash
clear

. demo-magic.sh

# hide the evidence
clear

## 1. Trigger Jobs (2000 jobs)

pe "curl -X POST -H 'Content-Type: application/json' -d @../../sailfish-py/body-small.json https://sailfish-gateway-rdlabs-experiment-cas-eu-west.apps.bfwn6g56.westeurope.aroapp.io/jobs"

# Now because CI is low in EU, The Dispatcher will decide to run the job locally.

# For demo purposes lets change the time, often time is correlated with the CI of the region

# If we change the time to 6pm in EU, the CI will be high in EU

# The dispatcher will decide to run the job in NA-West

# ALT TAB TO KEPLER (POWER MONITORING) 
TODO DEPLOY KEPLER
TODO MAKE IT POSSIBLE TO SWAP REGION (SIMPLE CONFIGMAP)
TODO MAKE IT POSSIBLE TO SCHEDULE LOCALLY

## 2. Carbon intensity is rigged: present EU is low in carbon intensity
### Show carbon intensity in region (dashboard)

## 3. Switch time to 6pm in eu, which means high carbon eu intenstiy, but low na-west
### display job migration

## 4. show compute intensity graph?


pe "echo 'do script' "