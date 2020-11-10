#!/bin/bash

## Init the environment
source config/env.sh

## Generator configuration
## We use generator-level n-events, which needs to be larger or equal to 
## the number of juggler events
export NEVENTS=1000
if [ ${JUGGLER_N_EVENTS} \> ${NEVENTS} ]; then
  NEVENTS=${JUGGLER_N_EVENTS}
fi

## Our random seed
export RNG_SEED=1

## Setup local environment
export DATA_PATH=$RESULTS_PATH/data/dvmp


EBEAM=
PBEAM=
DECAY=
CONFIG=

while [ $# -gt 0 ]; do
  key=$1
  case $key in
    --ebeam)
      EBEAM="$2"
      shift
      shift
      ;;
    --pbeam)
      PBEAM="$2"
      shift
      shift
      ;;
    --decay)
      DECAY="$2"
      shift
      shift
      ;;
    --config)
      CONFIG="$2"
      shift
      shift
      ;;
    *)
      echo "Unknown option $key to run_generator(), aborting..."
      exit 1
  esac
done

if [ -z $EBEAM ]; then
  echo "EBEAM not defined in run_generator, aborting..."
  exit 1
elif [ -z $PBEAM ]; then
  echo "PBEAM not defined in run_generator, aborting..."
  exit 1
elif [ -z $DECAY ]; then
  echo "DECAY not defined in run_generator, aborting..."
  exit 1
elif [ $DECAY != "electron" ] && [ $DECAY != "muon" ] ; then
  echo "Unknown decay channel $DECAY, aborting..."
  exit 1
elif [ -z $CONFIG ]; then
  echo "CONFIG not defined in run_generator, aborting..."
fi

pushd dvmp
FNAME=`scripts/print_fname.sh \
                  --ebeam $EBEAM \
                  --pbeam $PBEAM \
                  --decay $DECAY \
                  --config $CONFIG \
                  --type gen`
if [ -f "${DATA_PATH}/${FNAME}.hepmc" ]; then
  echo "Found cached generator output for $FNAME, no need to rerun"
  exit 
fi

echo "Generator output for $FNAME not found in cache, need to run generator"

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
CONFIG_IN="generator/${CONFIG}.json.in"
echo "Creating generator configuration file ${FNAME}.json"
if [ ! -f ${CONFIG_IN} ]; then
  echo "ERROR: cannot find master config file ${CONFIG_IN}"
  exit 1
fi
sed "s/@TAG@/${FNAME}/" $CONFIG_IN | \
  sed "s/@EBEAM@/${EBEAM}/" | \
  sed "s/@PBEAM@/${PBEAM}/" | \
  sed "s/@DECAY_LEPTON@/${DECAY_PID}/" | \
  sed "s/@BRANCHING@/${BRANCHING}/" > ${FNAME}.json

## New we can run the generator
echo "Running the generator"
lager -r ${RNG_SEED} -c ${FNAME}.json -e ${NEVENTS} -o .

## Finally, move relevant output into the artifacts directory
echo "Moving generator output into ${DATA_PATH}"
mkdir -p ${DATA_PATH}
for ext in hepmc json log root; do
  mv *.${FNAME}.*.${ext} ${DATA_PATH}/${FNAME}.${ext}
done
