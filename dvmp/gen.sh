#!/bin/bash

## =============================================================================
## Run a single instance of the DVMP generator (lAger)
## Runs in 5 steps:
##   1. Parse the command line and setup the environment
##   2. Check if we can load the requested file from the cache
##   3. Create our configuration fil
##   4. Run the actual generator
##   5. Finalize
## =============================================================================

## make sure we launch this script from the project root directory
PROJECT_ROOT="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"/..
pushd ${PROJECT_ROOT}

## =============================================================================
## Step 1: Setup the environment variables
##
## First parse the command line flags.
## This sets the following environment variables:
## - CONFIG:   The specific generator configuration
## - EBEAM:    The electron beam energy
## - PBEAM:    The ion beam energy
## - DECAY:    The decay particle for the generator
export REQUIRE_DECAY=1
source util/parse_cmd.sh $@

## To run the generator, we need the following global variables:
##
## - LOCAL_PREFIX:      Place to cache local packages and data
## - JUGGLER_N_EVENTS:  Number of events to process
## - JUGGLER_RNG_SEED:  Random seed for event generation.
##
## You can read config/env.sh for more in-depth explanations of the variables
## and how they can be controlled.
source config/env.sh

## We also need the following benchmark-specific variables:
##
## - BENCHMARK_TAG: Unique identified for this benchmark process.
## - DATA_PATH:     Place to store our persistent output artifacts.
##
## You can read dvmp/env.sh for more in-depth explanations of the variables.
source dvmp/env.sh

## Get a unique file name based on the configuration options
FNAME=`util/print_fname.sh \
                  --ebeam $EBEAM \
                  --pbeam $PBEAM \
                  --decay $DECAY \
                  --config $CONFIG \
                  --type gen`

## =============================================================================
## Step 2: Check if we really need to run, or can use the cache.
if [ -f "${DATA_PATH}/${FNAME}.hepmc" ]; then
  echo "Found cached generator output for $FNAME, no need to rerun"
  exit 
fi

echo "Generator output for $FNAME not found in cache, need to run generator"

## =============================================================================
## Step 3: Create generator configuration file

## process decay info
BRANCHING=
DECAY_PID=
if [ $DECAY = "electron" ]; then
  BRANCHING="0.05971"
  DECAY_PID="11"
elif [ $DECAY = "muon" ]; then
  BRANCHING="0.05961"
  DECAY_PID="13"
fi

## generate the config file for this generator setup
CONFIG_IN="${BENCHMARK_TAG}/generator/${CONFIG}.json.in"
echo "Creating generator configuration file ${FNAME}.json"
if [ ! -f ${CONFIG_IN} ]; then
  echo "ERROR: cannot find master config file ${CONFIG_IN}"
  exit 1
fi
sed "s/@TAG@/${FNAME}/" $CONFIG_IN | \
  sed "s/@EBEAM@/${EBEAM}/" | \
  sed "s/@PBEAM@/${PBEAM}/" | \
  sed "s/@DECAY_LEPTON@/${DECAY_PID}/" | \
  sed "s/@BRANCHING@/${BRANCHING}/" > .local/${FNAME}.json

## =============================================================================
## Step 4: Run the event generator
echo "Running the generator"
lager -r ${JUGGLER_RNG_SEED} -c .local/${FNAME}.json -e ${JUGGLER_N_EVENTS} -o ${LOCAL_PREFIX}
if [ "$?" -ne "0" ] ; then
  echo "ERROR running lAger"
  exit 1
fi

## =============================================================================
## Step 5: Finally, move relevant output into the artifacts directory and clean up
echo "Moving generator output into ${DATA_PATH}"
mkdir -p ${DATA_PATH}
for ext in hepmc json log root ; do
  mv ${LOCAL_PREFIX}/*.${FNAME}.*.${ext} ${DATA_PATH}/${FNAME}.${ext}
done
echo "Cleaning up"
rm .local/${FNAME}.json

## All done!
