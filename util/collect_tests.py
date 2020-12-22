#!/usr/bin/env python3

"""
Collect the json files from individual benchmark tests into
a larger json file that combines all benchmark information,
and do additional accounting for the benchmark.

Tests results are expected to have the following file name and directory
structure:
   results/<BENCHMARK_NAME>/<SOME_NAME>.json
or
   results/<BENCHMARK_NAME>/subdirectory/<SOME_NAME>.json

Internally, we will look for the "tests" keyword in each of these
files to identify them as benchmark components.
"""


