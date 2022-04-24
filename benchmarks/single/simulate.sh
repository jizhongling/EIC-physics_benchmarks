#!/bin/bash

source $(dirname $0)/common.sh $*

# Simulate
ddsim --runType run \
      --printLevel WARNING \
      --enableGun \
      --steeringFile ${JUGGLER_GEN_FILE} \
      --numberOfEvents ${JUGGLER_N_EVENTS} \
      --part.minimalKineticEnergy 1*TeV  \
      --filter.tracker edep0 \
      --compactFile ${DETECTOR_PATH}/${JUGGLER_DETECTOR}.xml \
      --outputFile  ${JUGGLER_SIM_FILE}
if [[ "$?" -ne "0" ]] ; then
  echo "ERROR running ddsim"
  exit 1
fi
