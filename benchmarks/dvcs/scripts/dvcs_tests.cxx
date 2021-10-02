#include <cmath>
#include <iostream>
#include <string>
#include <vector>

#include "ROOT/RDataFrame.hxx"

#include <nlohmann/json.hpp>
using json = nlohmann::json;

R__LOAD_LIBRARY(libfmt.so)
#include "fmt/core.h"
#include "fmt/color.h"

R__LOAD_LIBRARY(libeicd.so)
R__LOAD_LIBRARY(libDD4pod.so)

#include "dd4pod/Geant4ParticleCollection.h"
#include "eicd/TrackParametersCollection.h"
#include "eicd/ClusterCollection.h"
#include "eicd/ReconstructedParticleCollection.h"
#include "eicd/BasicParticleCollection.h"

using ROOT::RDataFrame;
using namespace ROOT::VecOps;

auto p_track = [](std::vector<eic::TrackParametersData> const& in) {
  std::vector<double> result;
  for (size_t i = 0; i < in.size(); ++i) {
    result.push_back(std::abs(1.0/(in[i].qOverP)));
  }
  return result;
};


auto pt  = [](std::vector<dd4pod::Geant4ParticleData> const& in){
  std::vector<float> result;
  for (size_t i = 0; i < in.size(); ++i) {
    result.push_back(std::sqrt(in[i].ps.x * in[i].ps.x + in[i].ps.y * in[i].ps.y));
  }
  return result;
};

auto momentum = [](std::vector<ROOT::Math::PxPyPzMVector> const& in) {
  std::vector<double> result;
  for (size_t i = 0; i < in.size(); ++i) {
   result.push_back(in[i].E());
  }
  return result;
};
auto theta = [](std::vector<ROOT::Math::PxPyPzMVector> const& in) {
  std::vector<double> result;
  for (size_t i = 0; i < in.size(); ++i) {
   result.push_back(in[i].Theta()*180/M_PI);
  }
  return result;
};
auto fourvec = [](ROOT::VecOps::RVec<dd4pod::Geant4ParticleData> const& in) {
  std::vector<ROOT::Math::PxPyPzMVector> result;
  ROOT::Math::PxPyPzMVector lv;
  for (size_t i = 0; i < in.size(); ++i) {
    lv.SetCoordinates(in[i].ps.x, in[i].ps.y, in[i].ps.z, in[i].mass);
    result.push_back(lv);
  }
  return result;
};
auto recfourvec = [](ROOT::VecOps::RVec<eic::ReconstructedParticleData> const& in) {
  std::vector<ROOT::Math::PxPyPzMVector> result;
  ROOT::Math::PxPyPzMVector lv;
  for (size_t i = 0; i < in.size(); ++i) {
    lv.SetCoordinates(in[i].p.x, in[i].p.y, in[i].p.z, in[i].mass);
    result.push_back(lv);
  }
  return result;
};

auto delta_p = [](const std::vector<double>& tracks, const std::vector<double>& thrown) {
  std::vector<double> res;
  for (const auto& p1 : thrown) {
    for (const auto& p2 : tracks) {
      res.push_back(p1 - p2);
    }
  }
  return res;
};


void dvcs_tests(const char* fname = "rec_dvcs.root"){

  fmt::print(fmt::emphasis::bold | fg(fmt::color::forest_green), "Running DVCS analysis...\n");

  // Run this in multi-threaded mode if desired
  ROOT::EnableImplicitMT();
  ROOT::RDataFrame df("events", fname);

  using ROOT::Math::PxPyPzMVector;
  PxPyPzMVector p_ebeam = {0,0,-10, 0.000511};
  PxPyPzMVector p_pbeam = {0,0,275,  0.938 };

  auto eprime = [](ROOT::VecOps::RVec<dd4pod::Geant4ParticleData> const& in) {
    for(const auto& p : in){
      if(p.pdgID == 11 ) {
        return PxPyPzMVector(p.ps.x,p.ps.y,p.ps.z,p.mass);
      }
    }
    return PxPyPzMVector(0,0,0,0);
  };
  auto q_vec = [=](PxPyPzMVector const& p) {
    return p_ebeam - p;
  };

  auto df0 = df.Define("isThrown", "mcparticles.genStatus == 1")
                 .Define("thrownParticles", "mcparticles[isThrown]")
                 .Define("thrownP", fourvec, {"thrownParticles"})
                 .Define("recP", recfourvec, {"ReconstructedParticles"})
                 .Define("NPart", "recP.size()")
                 .Define("p_thrown", momentum, {"thrownP"})
                 .Define("nTracks", "outputTrackParameters.size()")
                 .Define("p_track", p_track, {"outputTrackParameters"})
                 .Define("delta_p",delta_p, {"p_track", "p_thrown"})
                 .Define("eprime", eprime, {"thrownParticles"})
                 .Define("q",  q_vec, {"eprime"})
                 .Define("Q2", "-1.0*(q.Dot(q))");

  auto h_n_dummy = df0.Histo1D({"h_n_part", "; h_n_part n", 10, 0, 10}, "NPart");
  auto h_Q2      = df0.Histo1D({"h_Q2", "; Q^{2} [GeV^{2}/c^{2}]", 100, 0, 30}, "Q2");
  auto n_Q2      = df0.Filter("Q2>1").Count();
  auto n_tracks  = df0.Mean("nTracks");

  // ---------------------------
  // Do evaluation

  auto c = new TCanvas();
  h_Q2->DrawCopy();
  c->SaveAs("results/dvcs/Q2.png");
  c->SaveAs("results/dvcs/Q2.pdf");
  fmt::print("{} DVCS events\n",*n_Q2);
  fmt::print("{} tracks per event\n",*n_tracks);

  c = new TCanvas();
  h_n_dummy->DrawCopy();
  c->SaveAs("results/dvcs/n_dummy.png");
  //c->SaveAs("results/dvcs/n_dummy.pdf");

}
