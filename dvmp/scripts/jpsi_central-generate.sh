#!/bin/bash

## Init the environment
source config/env.sh

## Generator configuration
export NEVENTS=100
export RNG_SEED=1

export DVMP_RESULTS_PATH=$RESULTS_PATH/dvmp

export FNAME_EL="${DVMP_RESULTS_PATH}/jpsi_central_el-gen"
export FNAME_MU="${DVMP_RESULTS_PATH}/jpsi_central_mu-gen"

## Check if we already have our MC files in the cache
if [ -f "${FNAME_EL}.hepmc" ] && [ -f "${FNAME_MU}.hepmc"]; then
  echo "Found cached generator output, no need to rerun"
else
  echo "Need to generate our event sample"
  pushd dvmp

  ## First generate our actual configuration files. We run for both electron
  ## and muon configurations
  ./generator/config_jpsi_decay.sh -c generator/jpsi_central.json.in
  ## This generates our jpsi_central_el.json and jpsi_central_mu.json files

  ## Now we can run the generator in parallel for both configurations
  echo "Running the generator"
  lager -r ${RNG_SEED} -c jpsi_central_el.json -e ${NEVENTS} -o . &
  lager -r ${RNG_SEED} -c jpsi_central_mu.json -e ${NEVENTS} -o . &
  wait

  ## Finally, we move our output into the artifacts directory
  echo "Moving generator output into ${DVMP_RESULTS_PATH}"
  mkdir -p ${DVMP_RESULTS_PATH}
  mv *electron*.json ${FNAME_EL}.json
  mv *electron*.root ${FNAME_EL}.root
  mv *electron*.hepmc ${FNAME_EL}.hepmc
  mv *electron*.log ${FNAME_EL}.log
  mv *muon*.json ${FNAME_MU}.json
  mv *muon*.root ${FNAME_MU}.root
  mv *muon*.hepmc ${FNAME_MU}.hepmc
  mv *muon*.log ${FNAME_MU}.log
fi
