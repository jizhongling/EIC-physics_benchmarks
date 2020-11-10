#!/bin/bash

## Init the environment
source config/env.sh

## Maximum number of generators to run in parallel
export MT=10

## Generates different configurations from the master configuration
## for both electron and muon decay channels

echo "Generating DVMP event samples using lAger"

EBEAM=
PBEAM=
DECAYS=()
CONFS=()

while [ $# -gt 0 ]
do
  key="$1"
  case $key in
    --config)
      CONFS+=("$2")
      shift # past argument
      shift # past value
      ;;
    --decay)
      DECAYS+=("$2")
      shift # past argument
      shift # past value
      ;;
    --ebeam)
      EBEAM="$2"
      shift # past argument
      shift # past value
      ;;
    --pbeam)
      PBEAM="$2"
      shift # past argument
      shift # past value
      ;;
    *)    # unknown option
      echo "unknown option"
      exit 1
      ;;
  esac
done

if [ ${#CONFS[@]} -eq 0 ]; then
  echo "ERROR: need one or more config names: --config <config name> "
  exit 1
elif [ ${#DECAYS[@]} -eq 0 ]; then
  echo "ERROR: need one or more decay types: --decay muon/electron"
  exit 1
elif [ -z $EBEAM ]; then
  echo "ERROR: EBEAM not defined: --EBEAM <energy>"
  exit 1
elif [ -z $PBEAM ]; then
  echo "ERROR: PBEAM not defined: --PBEAM <energy>"
  exit 1
fi

## loop over all our configurations and run the generator in parallel

parallel -j ${MT} \
   "dvmp/scripts/run_generator_instance.sh --ebeam ${EBEAM} --pbeam ${PBEAM} --config {1} --decay {2}" \
  ::: "${CONFS[@]}" ::: "${DECAYS[@]}"

CONFIG_BASE=`basename ${CONFIG} .json.in`

echo "Event generation finished"
