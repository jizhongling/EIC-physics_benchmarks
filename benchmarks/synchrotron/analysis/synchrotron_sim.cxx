#include <cmath>
#include <iostream>
#include <string>
#include <vector>

#include "ROOT/RDataFrame.hxx"
#include "Math/Vector4D.h"
#include "TCanvas.h"
#include "TSystem.h"

#include <nlohmann/json.hpp>
using json = nlohmann::json;

R__LOAD_LIBRARY(libfmt.so)
#include "fmt/core.h"
#include "fmt/color.h"

R__LOAD_LIBRARY(libeicd.so)
R__LOAD_LIBRARY(libDD4pod.so)

#include "eicd/ReconstructedParticleCollection.h"

void synchrotron_sim(const char* fname = "sim_synchrotron.root"){

  fmt::print(fmt::emphasis::bold | fg(fmt::color::forest_green), "Running synchrotron analysis...\n");

  // Run this in multi-threaded mode if desired
  ROOT::EnableImplicitMT();
  ROOT::RDataFrame df("events", fname);

  // Detector version
  std::string detector_version("default");
  const char* juggler_detector_version = gSystem->Getenv("JUGGLER_DETECTOR_VERSION");
  if (juggler_detector_version) {
    detector_version = juggler_detector_version;
  }

  if (detector_version == "acadia") {
    // Define variables
    auto df0 = df
      .Define("n_VertexBarrelHits", "VertexBarrelHits.size()")
      .Define("n_VertexEndcapHits", "VertexEndcapHits.size()")
    ;
    auto n_VertexBarrelHits = df0.Mean("n_VertexBarrelHits");
    auto n_VertexEndcapHits = df0.Mean("n_VertexEndcapHits");
    std::cout << "n_VertexBarrelHits = " << *n_VertexBarrelHits << " / ev" << std::endl;
    std::cout << "n_VertexEndcapHits = " << *n_VertexEndcapHits << " / ev" << std::endl;
  } else if (detector_version == "canyonlands") {
    // Define variables
    auto df0 = df
      .Define("n_VertexBarrelHits", "VertexBarrelHits.size()")
    ;
    auto n_VertexBarrelHits = df0.Mean("n_VertexBarrelHits");
    std::cout << "n_VertexBarrelHits = " << *n_VertexBarrelHits << " / ev" << std::endl;
  } else {
    std::cout << "Detector version " << detector_version << " not supported in synchrotron_sim.cxx" << std::endl; 
  }
}
