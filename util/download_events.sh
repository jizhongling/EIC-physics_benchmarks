#!/bin/bash

## Init the environment
source config/env.sh

## Generates different configurations from the master configuration
## for both electron and muon decay channels

echo "Download generator artifacts for one or more of the physics processes"

PROCS=()
BRANCH="dvmp"

function print_the_help {
  echo "USAGE:    $0 [-c config [[-c config ...]] script1 [script2...]"
  echo "OPTIONS:"
  echo "          -p,--process  Physics process name (can be defined multiple
  times)."
  echo "          -b,--branch   Git branch to download artifacts from (D:
  $BRANCH)"
  echo "          -h,--help     Print this message"
  echo ""
  echo "  This script will download the relevant generator artifacts needed"
  echo "  for local testing of the benchmarks."
  exit
}


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
    -h|--help)
      print_the_help
      shift
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
  echo "Unpacking artifacts..."
  unzip -u results.zip
  echo "Cleaning up..."
  rm results.zip
done
echo "All done"
