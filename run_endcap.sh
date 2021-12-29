#!/bin/bash

function print_the_help {
  echo "USAGE: ${0} -j <job> -n <nevents> -e <energy> -a <angle> -t <nametag> -p <particle> "
  echo "  OPTIONS: "
  echo "    -j,--job         Index of job"
  echo "    -n,--nevents     Number of events in eatch batch"
  echo "    -e,--energy      Energy list in GeV"
  echo "    -a,--angle       Input angle in degree"
  echo "    -t,--nametag     Name tag"
  echo "    -p,--particle    Particle type"
  echo "                     Allowed types: pi0, pi+, pi-, kaon0, kaon+, kaon-, proton, neutron, e-, e+, mu-, mu+, gamma"
  exit
}

POSITIONAL=()
while [[ $# -gt 0 ]]
do
  key="$1"

  case $key in
    -h|--help)
      shift # past argument
      print_the_help
      ;;
    -j|--job)
      export PROC="$2"
      shift # past argument
      shift # past value
      ;;
    -n|--nevents)
      export JUGGLER_N_EVENTS="$2"
      shift # past argument
      shift # past value
      ;;
    -e|--energy)
      export ENERGY="$(( ( $2 / 10 + 1 ) * 2 ))"
      shift # past argument
      shift # past value
      ;;
    -a|--angle)
      ANGLE="$(( ( $2 % 10 + 1 ) * 5 ))"
      shift # past argument
      shift # past value
      ;;
    -t|--nametag)
      nametag="$2"
      shift # past argument
      shift # past value
      ;;
    -p|--particle)
      particle="$2"
      shift # past argument
      shift # past value
      ;;
    *) # unknown option
      #POSITIONAL+=("$1") # save it in an array for later
      echo "unknown option $1"
      print_the_help
      shift # past argument
      ;;
  esac
done
set -- "${POSITIONAL[@]}" # restore positional parameters

export PYTHONPATH=${ATHENA_PREFIX}/python:${PYTHONPATH}
export DETECTOR_PATH=${ATHENA_PREFIX}/../athena
export JUGGLER_DETECTOR=athena
export JUGGLER_DETECTOR_VERSION=default
export JUGGLER_COMPACT_PATH=${DETECTOR_PATH}/${JUGGLER_DETECTOR}.xml

if [[ ! -n "${JUGGLER_N_EVENTS}" ]] ; then
  export JUGGLER_N_EVENTS=1000
fi

if [[ ! -n "${ENERGY}" ]] ; then
  export ENERGY=10
fi

OUTDIR=${SPIN}/data/eic/${nametag}
mkdir -p ${OUTDIR}
SKIP_N_EVENTS=$(( 0 * PROC * JUGGLER_N_EVENTS ))
export GEN_FILE="${OUTDIR}/gen_${ENERGY}GeV_${ANGLE}deg.hepmc"
export JUGGLER_SIM_FILE="${OUTDIR}/sim_${ENERGY}GeV_${ANGLE}deg.root"
export JUGGLER_REC_FILE="${OUTDIR}/rec_${ENERGY}GeV_${ANGLE}deg.root"

echo "Number of events: ${JUGGLER_N_EVENTS}"
echo "Skip number of events: ${SKIP_N_EVENTS}"
echo "Energy list: ${ENERGY}"
echo "Detector path: ${JUGGLER_COMPACT_PATH}"

# Generate the input events
python scripts/gen_particles.py ${GEN_FILE} -n ${JUGGLER_N_EVENTS}\
    --angmin ${ANGLE} --angmax ${ANGLE} --parray ${ENERGY} --particles="${particle}"
if [[ "$?" -ne "0" ]] ; then
  echo "ERROR running script: generating input events"
  exit 1
fi

ls -lh ${GEN_FILE}

# Run geant4 simulations
npsim --runType batch \
      -v WARNING \
      --part.minimalKineticEnergy "0.5*MeV" \
      --physics.list "FTFP_BERT_HP" \
      --numberOfEvents ${JUGGLER_N_EVENTS} \
      --skipNEvents ${SKIP_N_EVENTS} \
      --compactFile ${JUGGLER_COMPACT_PATH} \
      --inputFiles ${GEN_FILE} \
      --outputFile ${JUGGLER_SIM_FILE}
#-G --gun.particle "${particle}" --gun.energy "${ENERGY}*GeV" --gun.position "2.5025*cm 2.4747*cm -8.5*cm" --gun.direction "0 0.3420201433 0.9396926208" \

if [[ "$?" -ne "0" ]] ; then
  echo "ERROR running npdet"
  exit 1
fi

rootls -t "${JUGGLER_SIM_FILE}"

# Run Juggler
gaudirun.py options/reconstruction.hcal.py
if [[ "$?" -ne "0" ]] ; then
  echo "ERROR running juggler"
  exit 1
fi
