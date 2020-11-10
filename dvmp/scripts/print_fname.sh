#!/bin/bash

## Simple script to output a unified file name based on a set of data options

EBEAM=
PBEAM=
DECAY=
CONFIG=
TYPE=

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
    --type)
      TYPE="$2"
      shift
      shift
      ;;
    *)
      echo "Unknown option $key to print_fname, aborting..."
      exit 1
  esac
done

if [ -z $EBEAM ]; then
  echo "EBEAM not defined in print_fname, aborting..."
  exit 1
elif [ -z $PBEAM ]; then
  echo "PBEAM not defined in print_fname, aborting..."
  exit 1
elif [ -z $DECAY ]; then
  echo "DECAY not defined in print_fname, aborting..."
  exit 1
elif [ -z $CONFIG ]; then
  echo "CONFIG not defined in print_fname, aborting..."
elif [ -z $TYPE ]; then
  echo "TYPE not defined in print_fname, aborting..."
fi

echo "${CONFIG}_${DECAY}-${EBEAM}on${PBEAM}-${TYPE}"
