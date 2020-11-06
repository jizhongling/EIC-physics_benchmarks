#!/bin/bash

## Generates different configurations from the master configuration
## for both electron and muon decay channels

echo "Generating generator configuration files for J/psi -> e+e- and mu+mu-"

CONFIG=

POSITIONAL=()
while [[ $# -gt 0 ]]
do
  key="$1"

  case $key in
    -c|--config)
      CONFIG="$2"
      shift # past argument
      shift # past value
      ;;
    *)    # unknown option
      echo "unknown option"
      exit 1
      shift # past argument
      ;;
  esac
done
set -- "${POSITIONAL[@]}" # restore positional parameters

if [[ -z ${CONFIG} ]] ; then
  echo  " ERROR: need argument -c/--config <config file> "
  exit 1
fi
if [[ ! -f ${CONFIG} ]] ; then
  echo " ERROR: cannot find config input file ${CONFIG}"
  exit 1
fi

CONFIG_BASE=`basename ${CONFIG} .json.in`

echo "Generating ${CONFIG_BASE}_el.json"
sed "s/@TAG@/electron/" ${CONFIG} | \
  sed "s/@DECAY_LEPTON@/11/" | sed "s/@BRANCHING@/0.05971/" > ${CONFIG_BASE}_el.json
echo "Generating ${CONFIG_BASE}_mu.json"
sed "s/@TAG@/muon/" ${CONFIG} | \
  sed "s/@DECAY_LEPTON@/13/" | sed "s/@BRANCHING@/0.05961/" > ${CONFIG_BASE}_mu.json

echo "Configuration generation finished."
