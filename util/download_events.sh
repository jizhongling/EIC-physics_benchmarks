#!/bin/bash

## Init the environment
source config/env.sh

## Generates different configurations from the master configuration
## for both electron and muon decay channels

echo "Download generator artifacts for one or more of the physics processes"

PROCS=()
BRANCH="dvmp"

while [ $# -gt 0 ]
do
  key="$1"
  case $key in
    -p|--process)
      PROCS+=("$2")
      shift # past argument
      shift # past value
      ;;
    --branch)
      BRANCH="$2"
      shift # past argument
      shift # past value
      ;;
    *)    # unknown option
      echo "unknown option"
      exit 1
      ;;
  esac
done

if [ ${#PROCS[@]} -eq 0 ]; then
  echo "ERROR: need one or more processes: -p <process name> "
  exit 1
fi

for proc in ${PROCS[@]}; do
  echo "Dowloading artifacts for $proc (branch: $BRANCH)"
  wget https://eicweb.phy.anl.gov/EIC/benchmarks/physics_benchmarks/-/jobs/artifacts/$BRANCH/download?job=${proc}:jpsi_central:generate -O results.zip
  unzip -u results.zip
  rm results.zip
done
