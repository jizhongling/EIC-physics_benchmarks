#!/bin/bash

source $(dirname $0)/common.sh $*

# Analyze
root -l -b -q "benchmarks/single/analysis/analyze.cxx+(\"${JUGGLER_REC_FILE}\")"
if [[ "$?" -ne "0" ]] ; then
  echo "ERROR analysis failed"
  exit 1
fi
