#include "ROOT/RDataFrame.hxx"
#include <iostream>

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

std::vector<float> pt (std::vector<dd4pod::Geant4ParticleData> const& in){
  std::vector<float> result;
  for (size_t i = 0; i < in.size(); ++i) {
    result.push_back(std::sqrt(in[i].psx * in[i].psx + in[i].psy * in[i].psy));
  }
  return result;
}

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

int rec_dis_electrons(const char* fname = "topside/rec_central_electrons.root")
{

  ROOT::EnableImplicitMT();
  ROOT::RDataFrame df("events", fname);

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
                 .Define("delta_p2",delta_p, {"p_track2", "p_thrown"});

  auto h_nTracks = df0.Histo1D({"h_nTracks", "; N tracks ", 10, 0, 10}, "nTracks");
  auto h_pTracks = df0.Histo1D({"h_pTracks", "; GeV/c ", 100, 0, 10}, "p_track");

  auto h_delta_p  = df0.Histo1D({"h_delta_p", "; GeV/c ",  100, -10, 10}, "delta_p");
  auto h_delta_p1 = df0.Histo1D({"h_delta_p1", "; GeV/c ", 100, -10, 10}, "delta_p1");
  auto h_delta_p2 = df0.Histo1D({"h_delta_p2", "; GeV/c ", 100, -10, 10}, "delta_p2");

  auto c = new TCanvas();

  h_nTracks->DrawCopy();
  c->SaveAs("results/dis/rec_central_electrons_nTracks.png");
  c->SaveAs("results/dis/rec_central_electrons_nTracks.pdf");

  h_pTracks->DrawCopy();
  c->SaveAs("results/dis/rec_central_electrons_pTracks.png");
  c->SaveAs("results/dis/rec_central_electrons_pTracks.pdf");

  THStack * hs = new THStack("hs_delta_p","; GeV/c "); 
  TH1D* h1 = (TH1D*) h_delta_p->Clone();
  hs->Add(h1);
  h1 = (TH1D*) h_delta_p1->Clone();
  h1->SetLineColor(2);
  hs->Add(h1);
  h1 = (TH1D*) h_delta_p2->Clone();
  h1->SetLineColor(4);
  h1->SetFillStyle(3001);
  h1->SetFillColor(4);
  hs->Add(h1);
  hs->Draw("nostack");
  c->SaveAs("results/dis/rec_central_electrons_delta_p.png");
  c->SaveAs("results/dis/rec_central_electrons_delta_p.pdf");

  return 0;
}
