#!/bin/bash

if [[ ! -n  "${JUGGLER_N_EVENTS}" ]] ; then 
  export JUGGLER_N_EVENTS=100
fi

export JUGGLER_FILE_NAME_TAG="${1:-e-_1GeV_45to135deg}"
export JUGGLER_GEN_FILE="benchmarks/single/${JUGGLER_FILE_NAME_TAG}.steer"
export JUGGLER_SIM_FILE="sim_${JUGGLER_FILE_NAME_TAG}.root"
export JUGGLER_REC_FILE="rec_${JUGGLER_FILE_NAME_TAG}.root"

# Simulate
npsim --runType run \
      --printLevel WARNING \
      --enableGun \
      --steeringFile ${JUGGLER_GEN_FILE} \
      --numberOfEvents ${JUGGLER_N_EVENTS} \
      --part.minimalKineticEnergy 1*TeV  \
      --compactFile ${DETECTOR_PATH}/${JUGGLER_DETECTOR}.xml \
      --outputFile  ${JUGGLER_SIM_FILE}
if [[ "$?" -ne "0" ]] ; then
  echo "ERROR running npsim"
  exit 1
fi

# Reconstruct
for rec in options/*.py ; do
  unset tag
  [[ $(basename ${rec} .py) =~ (.*)\.(.*) ]] && tag=".${BASH_REMATCH[2]}"
  JUGGLER_REC_FILE=${JUGGLER_REC_FILE/.root/${tag:-}.root} \
    gaudirun.py ${rec}
  if [[ "$?" -ne "0" ]] ; then
    echo "ERROR running juggler"
    exit 1
  fi
done

# Analysis
root -l -b -q "benchmarks/single/analysis/analyze.cxx+(\"${JUGGLER_REC_FILE}\")"
if [[ "$?" -ne "0" ]] ; then
  echo "ERROR analysis failed"
  exit 1
fi
