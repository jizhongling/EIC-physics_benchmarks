if [[ ! -n  "${JUGGLER_N_EVENTS}" ]] ; then 
  export JUGGLER_N_EVENTS=100
fi

export JUGGLER_FILE_NAME_TAG="${1:-e-_1GeV_45to135deg}"
export JUGGLER_GEN_FILE="benchmarks/single/${JUGGLER_FILE_NAME_TAG}.steer"
export JUGGLER_SIM_FILE="sim_output/sim_${JUGGLER_FILE_NAME_TAG}.edm4hep.root"
export JUGGLER_REC_FILE="sim_output/rec_${JUGGLER_FILE_NAME_TAG}.root"
