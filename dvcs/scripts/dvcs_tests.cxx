#include <ROOT/RDataFrame.hxx>
#include <cmath>
#include "fmt/color.h"
#include "fmt/core.h"
#include <iostream>
#include <string>
#include <vector>
#include <nlohmann/json.hpp>
using json = nlohmann::json;

#include "dd4pod/Geant4ParticleCollection.h"
#include "eicd/TrackParametersCollection.h"
#include "eicd/ClusterCollection.h"
#include "eicd/ClusterData.h"

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
    result.push_back(std::sqrt(in[i].psx * in[i].psx + in[i].psy * in[i].psy));
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
    lv.SetCoordinates(in[i].psx, in[i].psy, in[i].psz, in[i].mass);
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
        return PxPyPzMVector(p.psx,p.psy,p.psz,p.mass);
      }
    }
    return PxPyPzMVector(0,0,0,0);
  };
  auto q_vec = [=](PxPyPzMVector const& p) {
    return p_ebeam - p;
  };

  auto df0 = df.Define("isThrown", "mcparticles2.genStatus == 1")
                 .Define("thrownParticles", "mcparticles2[isThrown]")
                 .Define("thrownP", fourvec, {"thrownParticles"})
                 .Define("p_thrown", momentum, {"thrownP"})
                 .Define("nTracks", "outputTrackParameters.size()")
                 .Define("p_track", p_track, {"outputTrackParameters"})
                 .Define("p_track1", p_track, {"outputTrackParameters1"})
                 .Define("p_track2", p_track, {"outputTrackParameters2"})
                 .Define("delta_p",delta_p, {"p_track", "p_thrown"})
                 .Define("delta_p1",delta_p, {"p_track1", "p_thrown"})
                 .Define("delta_p2",delta_p, {"p_track2", "p_thrown"})
                 .Define("eprime", eprime, {"thrownParticles"})
                 .Define("q",  q_vec, {"eprime"})
                 .Define("Q2", "-1.0*(q.Dot(q))");

  auto h_Q2 = df0.Histo1D({"h_Q2", "; Q^{2} [GeV^{2}/c^{2}]", 100, 0, 30}, "Q2");
  auto n_Q2 = df0.Filter("Q2>1").Count();

  auto c = new TCanvas();
  h_Q2->DrawCopy();
  c->SaveAs("results/dvcs/Q2.png");
  c->SaveAs("results/dvcs/Q2.pdf");
  fmt::print("{} DVCS events\n",*n_Q2);

  // write output results to json file
  json j;
  j["Q2 cut"]["pass"] = *n_Q2;
  j["Q2 cut"]["fail"] = 1;
  std::ofstream o("results/dvcs/dvcs_tests.json");
  o << std::setw(4) << j << std::endl;
  //df0.Snapshot("testing","derp.root");
}
