#!/bin/bash

## =============================================================================
## Simple script to output a unified file name based on a set of data options
## Note: this file name will not have an extension, as it is mean to be used as
##       a file name root.

function print_the_help {
  echo "USAGE:    print_fname [arguments]"
  echo "REQUIRED ARGUMENTS:"
  echo "          --ebeam       Electron beam energy"
  echo "          --pbeam       Ion beam energy"
  echo "          --config      Generator configuration identifier"
  echo "          --type        What type of output file is this? (e.g. sim, rec, ...)"
  echo "OPTIONAL ARGUMENTS:"
  echo "          --decay       Specific decay particle (if applicable)."
  echo "          -h,--help     Print this message"
  echo ""
  echo "  This script will generate a unique file name for the benchmark output."
  exit
}

## =============================================================================
## Process the command line arguments

## Required variables
EBEAM=
PBEAM=
CONFIG=
TYPE=

## Optional variables
DECAY=

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
    --decay)
      DECAY="$2"
      shift
      shift
      ;;
    -h|--help)
      print_the_help
      exit 0
      ;;
    *)
      echo "Unknown option $key to print_fname, aborting..."
      exit 1
  esac
done

if [ -z $EBEAM ]; then
  echo "EBEAM not defined in print_fname, aborting..."
  print_the_help
  exit 1
elif [ -z $PBEAM ]; then
  echo "PBEAM not defined in print_fname, aborting..."
  print_the_help
  exit 1
elif [ -z $CONFIG ]; then
  echo "CONFIG not defined in print_fname, aborting..."
  print_the_help
  exit 1
elif [ -z $TYPE ]; then
  echo "TYPE not defined in print_fname, aborting..."
  print_the_help
  exit 1
fi


## =============================================================================
## Generate a unique identifier based on the configuration arguments

## Add decay info to CONFIG if requested
if [ ! -z $DECAY ]; then
  CONFIG=${CONFIG}_${DECAY}
fi

echo "${TYPE}-${CONFIG}-${EBEAM}on${PBEAM}"

## all done.
