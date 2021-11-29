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

#include "eicd/InclusiveKinematicsCollection.h"
#include "eicd/ReconstructedParticleCollection.h"

void tcs_tests(const char* fname = "rec_tcs.root"){

  fmt::print(fmt::emphasis::bold | fg(fmt::color::forest_green), "Running TCS analysis...\n");

  // Run this in multi-threaded mode if desired
  ROOT::EnableImplicitMT();
  ROOT::RDataFrame df("events", fname);

  auto df0 = df.Define("n_parts", "ReconstructedParticles.size()")
               .Define("isQ2gt1", "InclusiveKinematicsTruth.Q2 > 1.0")
               .Define("n_Q2gt1", "isQ2gt1.size()");

  auto h_n_parts = df0.Histo1D({"h_n_parts", "; h_n_parts n", 10, 0, 10}, "n_parts");
  auto h_Q2      = df0.Histo1D({"h_Q2", "; Q^{2} [GeV^{2}/c^{2}]", 100, 0, 30}, "InclusiveKinematicsTruth.Q2");
  auto h_ff_status = df0.Histo1D({"h_ff_status", "; FF status", 10, -0.5, 9.5}, "ReconstructedFFParticles.status");
  auto n_Q2gt1   = df0.Mean("n_Q2gt1");
  auto n_parts   = df0.Mean("n_parts");

  // ---------------------------
  // Do evaluation

  auto c = new TCanvas();
  h_Q2->DrawCopy();
  c->SaveAs("results/tcs/Q2.png");
  c->SaveAs("results/tcs/Q2.pdf");
  fmt::print("{} TCS events Q2>1\n",*n_Q2gt1);
  fmt::print("{} tracks per event\n",*n_parts);

  c = new TCanvas();
  h_n_parts->DrawCopy();
  c->SaveAs("results/tcs/n_parts.png");
  c->SaveAs("results/tcs/n_parts.pdf");

  c = new TCanvas();
  h_ff_status->DrawCopy();
  c->SaveAs("results/tcs/ff_status.png");
  c->SaveAs("results/tcs/ff_status.pdf");
}
