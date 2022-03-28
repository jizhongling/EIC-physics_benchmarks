#!/bin/bash

## =============================================================================
## Run the DVMP benchmarks in 5 steps:
## 1. Parse the command line and setup environment
## 2. Detector simulation through ddsim
## 3. Digitization and reconstruction through Juggler
## 4. Root-based Physics analyses
## 5. Finalize
## =============================================================================

## make sure we launch this script from the project root directory
PROJECT_ROOT="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"/../..
pushd ${PROJECT_ROOT}

echo "Running the DVMP benchmarks"


## =============================================================================
## Step 1: Setup the environment variables
##
## First parse the command line flags.
## This sets the following environment variables:
## - CONFIG:   The specific generator configuration
## - EBEAM:    The electron beam energy
## - PBEAM:    The ion beam energy
## - DECAY:    The decay particle for the generator
## - LEADING:  Leading particle of interest (J/psi)
export REQUIRE_DECAY=1
export REQUIRE_LEADING=1
source parse_cmd.sh $@

## We also need the following benchmark-specific variables:
##
## - BENCHMARK_TAG: Unique identified for this benchmark process.
## - BEAM_TAG:      Identifier for the chosen beam configuration
## - INPUT_PATH:    Path for generator-level input to the benchmarks
## - TMP_PATH:      Path for temporary data (not exported as artifacts)
## - RESULTS_PATH:  Path for benchmark output figures and files
##
## You can read dvmp/env.sh for more in-depth explanations of the variables.
source benchmarks/dvmp/env.sh

## Get a unique file names based on the configuration options
GEN_FILE=${INPUT_PATH}/gen-${CONFIG}_${DECAY}_${JUGGLER_N_EVENTS}.hepmc

SIM_FILE=${TMP_PATH}/sim-${CONFIG}_${DECAY}.edm4hep.root
SIM_LOG=${TMP_PATH}/sim-${CONFIG}_${DECAY}.log


REC_FILE=${TMP_PATH}/rec-${CONFIG}_${DECAY}.root
REC_LOG=${TMP_PATH}/sim-${CONFIG}_${DECAY}.log

PLOT_TAG=${CONFIG}_${DECAY}

## =============================================================================
## Step 2: Run the simulation
echo "Running Geant4 simulation"
ls -lrth 
ls -lrth input
echo ${TMP_PATH}
ls -lrth ${TMP_PATH}
ddsim --runType batch \
      --part.minimalKineticEnergy 100*GeV  \
      --filter.tracker edep0 \
      -v WARNING \
      --numberOfEvents ${JUGGLER_N_EVENTS} \
      --compactFile ${DETECTOR_PATH}/${JUGGLER_DETECTOR}.xml \
      --inputFiles ${GEN_FILE} \
      --outputFile ${SIM_FILE}
if [ "$?" -ne "0" ] ; then
  echo "ERROR running ddsim"
  exit 1
fi

## =============================================================================
## Step 3: Run digitization & reconstruction
echo "Running the digitization and reconstruction"
## FIXME Need to figure out how to pass file name to juggler from the commandline
## the tracker_reconstruction.py options file uses the following environment
## variables:
## - JUGGLER_SIM_FILE:    input detector simulation
## - JUGGLER_REC_FILE:    output reconstructed data
## - JUGGLER_N_EVENTS:    number of events to process (part of global environment)
## - JUGGLER_DETECTOR:    detector package (part of global environment)
export JUGGLER_SIM_FILE=${SIM_FILE}
export JUGGLER_REC_FILE=${REC_FILE}
for rec in options/*.py ; do
  unset tag
  [[ $(basename ${rec} .py) =~ (.*)\.(.*) ]] && tag=".${BASH_REMATCH[2]}"
  JUGGLER_REC_FILE=${JUGGLER_REC_FILE/.root/${tag:-}.root} \
    gaudirun.py ${rec}
  if [ "$?" -ne "0" ] ; then
    echo "ERROR running juggler, both attempts failed"
    exit 1
  fi
done

## =============================================================================
## Step 4: Analysis

## write a temporary configuration file for the analysis script
CONFIG="${TMP_PATH}/${PLOT_TAG}.json"
cat << EOF > ${CONFIG}
{
  "rec_file": "${REC_FILE}",
  "vm_name": "${LEADING}",
  "decay": "${DECAY}",
  "detector": "${JUGGLER_DETECTOR}",
  "output_prefix": "${RESULTS_PATH}/${PLOT_TAG}",
  "test_tag": "${LEADING}_${DECAY}_${BEAM_TAG}"
}
EOF
#cat ${CONFIG}

## run the analysis script with this configuration
root -b -q "benchmarks/dvmp/analysis/vm_mass.cxx+(\"${CONFIG}\")"
if [ "$?" -ne "0" ] ; then
  echo "ERROR running vm_mass script"
  exit 1
fi
root -b -q "benchmarks/dvmp/analysis/vm_invar.cxx+(\"${CONFIG}\")"
if [ "$?" -ne "0" ] ; then
  echo "ERROR running vm_invar script"
  exit 1
fi

## =============================================================================
## Step 5: finalize
echo "Finalizing DVMP benchmark"

## Copy over reconsturction artifacts as long as we don't have
## too many events
if [ "${JUGGLER_N_EVENTS}" -lt "500" ] ; then 
  cp ${REC_FILE} ${RESULTS_PATH}
fi

## Always move over log files to the results path
mv ${REC_LOG} ${RESULTS_PATH}


## cleanup output files
#rm -f ${REC_FILE} ${SIM_FILE} ## --> not needed for CI

## =============================================================================
## All done!
echo "DVMP benchmarks complete"
