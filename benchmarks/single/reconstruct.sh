#!/bin/bash

source $(dirname $0)/common.sh $*

# Reconstruct
for rec in options/*.py ; do
  unset tag
  [[ $(basename ${rec} .py) =~ (.*)\.(.*) ]] && tag=".${BASH_REMATCH[2]}"
  JUGGLER_REC_FILE=${JUGGLER_REC_FILE/.root/${tag:-}.root} \
    gaudirun.py ${JUGGLER_GAUDI_OPTIONS:-} ${rec}
  if [[ "$?" -ne "0" ]] ; then
    echo "ERROR running juggler"
    exit 1
  fi
done
