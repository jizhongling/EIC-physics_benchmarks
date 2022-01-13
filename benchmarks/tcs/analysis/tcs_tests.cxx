#include <cmath>
#include <iostream>
#include <string>
#include <vector>

#include "ROOT/RDataFrame.hxx"
#include "Math/Vector4D.h"
#include "TCanvas.h"
#include "TLegend.h"

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

  auto ff_theta_mrad = [] (
      const std::vector<eic::ReconstructedParticleData>& v,
      const int16_t status
  ) -> std::vector<float> {
    std::vector<float> theta;
    for (const auto& p: v)
      if (p.status == status)
        theta.push_back(1000. * p.direction.theta);
    return theta;
  };

  auto df0 = df.Define("n_parts", "ReconstructedParticles.size()")
               .Define("isQ2gt1", "InclusiveKinematicsTruth.Q2 > 1.0")
               .Define("n_Q2gt1", "isQ2gt1.size()")
               .Define("ff_theta_mrad_B0", [&](const std::vector<eic::ReconstructedParticleData>& v){return ff_theta_mrad(v,1);}, {"ReconstructedFFParticles"})
               .Define("ff_theta_mrad_RP", [&](const std::vector<eic::ReconstructedParticleData>& v){return ff_theta_mrad(v,2);}, {"ReconstructedFFParticles"})
               .Define("ff_theta_mrad_OMD",[&](const std::vector<eic::ReconstructedParticleData>& v){return ff_theta_mrad(v,3);}, {"ReconstructedFFParticles"})
               .Define("ff_theta_mrad_ZDC",[&](const std::vector<eic::ReconstructedParticleData>& v){return ff_theta_mrad(v,4);}, {"ReconstructedFFParticles"})
               ;

  auto h_n_parts = df0.Histo1D({"h_n_parts", "; h_n_parts n", 10, 0, 10}, "n_parts");
  auto h_Q2      = df0.Histo1D({"h_Q2", "; Q^{2} [GeV^{2}/c^{2}]", 100, 0, 30}, "InclusiveKinematicsTruth.Q2");
  auto h_FF      = df0.Histo1D({"h_FF", "; FF status", 10, -0.5, 9.5}, "ReconstructedFFParticles.status");
  auto h_FF_B0   = df0.Histo1D({"h_FF_B0",  "; FF B0 Theta [mrad]",  100, 0.0, 25.0}, "ff_theta_mrad_B0");
  auto h_FF_RP   = df0.Histo1D({"h_FF_RP",  "; FF RP Theta [mrad]",  100, 0.0, 25.0}, "ff_theta_mrad_RP");
  auto h_FF_OMD  = df0.Histo1D({"h_FF_OMD", "; FF OMD Theta [mrad]", 100, 0.0, 25.0}, "ff_theta_mrad_OMD");
  auto h_FF_ZDC  = df0.Histo1D({"h_FF_ZDC", "; FF ZDC Theta [mrad]", 100, 0.0, 25.0}, "ff_theta_mrad_ZDC");
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
  h_FF->DrawCopy();
  c->SaveAs("results/tcs/ff.png");
  c->SaveAs("results/tcs/ff.pdf");

  c = new TCanvas();
  h_FF_B0->SetLineColor(1);
  h_FF_B0->DrawCopy();
  h_FF_RP->SetLineColor(2);
  h_FF_RP->DrawCopy("same");
  h_FF_OMD->SetLineColor(3);
  h_FF_OMD->DrawCopy("same");
  h_FF_ZDC->SetLineColor(4);
  h_FF_ZDC->DrawCopy("same");
  auto legend = new TLegend(0.1,0.7,0.48,0.9);
  legend->AddEntry(h_FF_B0.GetPtr(),  "B0",  "L");
  legend->AddEntry(h_FF_RP.GetPtr(),  "RP",  "L");
  legend->AddEntry(h_FF_OMD.GetPtr(), "OMD", "L");
  legend->AddEntry(h_FF_ZDC.GetPtr(), "ZDC", "L");
  legend->Draw();
  c->SaveAs("results/tcs/ff_theta.png");
  c->SaveAs("results/tcs/ff_theta.pdf");
}
