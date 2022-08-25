#include <cmath>
#include <iostream>
#include <string>
#include <vector>

#include "ROOT/RDataFrame.hxx"
#include "Math/Vector4D.h"
#include "TCanvas.h"

#include <nlohmann/json.hpp>
using json = nlohmann::json;

R__LOAD_LIBRARY(libfmt.so)
#include "fmt/core.h"
#include "fmt/color.h"

R__LOAD_LIBRARY(libeicd.so)
R__LOAD_LIBRARY(libDD4pod.so)

#include "eicd/ReconstructedParticleCollection.h"

void synchrotron_raw(const char* fname = "rec_synchrotron.raw.root"){

  fmt::print(fmt::emphasis::bold | fg(fmt::color::forest_green), "Running synchrotron analysis...\n");

  // Run this in multi-threaded mode if desired
  ROOT::EnableImplicitMT();
  ROOT::RDataFrame df("events", fname);

}
