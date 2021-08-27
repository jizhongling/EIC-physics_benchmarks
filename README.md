Physics Benchmarks for the EIC
==============================

![pipeline status](https://eicweb.phy.anl.gov/EIC/benchmarks/physics_benchmarks/badges/master/pipeline.svg)

## Running Locally

### Local development example

Here we setup to use our local build of the `juggler` library.
First set some environment variables.
```
export JUGGLER_INSTALL_PREFIX=$HOME/stow/juggler
export JUGGLER_DETECTOR=athena   # athena is the default
export BEAMLINE_CONFIG=ip6       # ip6 is the default
```


```
git@eicweb.phy.anl.gov:EIC/benchmarks/physics_benchmarks.git && cd physics_benchmarks
git clone https://eicweb.phy.anl.gov/EIC/benchmarks/common_bench.git setup
source setup/bin/env.sh && ./setup/bin/install_common.sh
source .local/bin/env.sh && build_detector.sh
mkdir_local_data_link sim_output
mkdir -p results
mkdir -p config

```


## Common bench

See [common_bench](https://eicweb.phy.anl.gov/EIC/benchmarks/common_bench) for details.



## Adding new benchmarks

### Pass/Fail tests

- Create a script that returns exit status 0 for success.
- Any non-zero value will be considered failure.
- Script  

