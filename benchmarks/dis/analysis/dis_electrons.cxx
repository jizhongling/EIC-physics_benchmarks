#include "common_bench/benchmark.h"
#include "common_bench/mt.h"
#include "common_bench/util.h"

#include <cmath>
#include <fstream>
#include <iostream>
#include <string>
#include <vector>
#include <algorithm>
#include <utility>

#include "ROOT/RDataFrame.hxx"
#include <TH1D.h>
#include <TFitResult.h>
#include <TRandom3.h>

#include "fmt/color.h"
#include "fmt/core.h"

#include "nlohmann/json.hpp"
#include "eicd/ReconstructedParticleData.h"

// Get a vector of 4-momenta from the reconstructed data.
inline auto momenta_from_reconstruction(const std::vector<eic::ReconstructedParticleData>& parts)
{
  std::vector<ROOT::Math::PxPyPzEVector> momenta{parts.size()};
  // transform our reconstructed particle data into 4-momenta
  std::transform(parts.begin(), parts.end(), momenta.begin(), [](const auto& part) {
    return ROOT::Math::PxPyPzEVector{part.p.x, part.p.y, part.p.z, part.energy};
  });
  return momenta;
}

// Convert PxPyPzMVector to PxPyPzEVector
inline auto convertMtoE(const std::vector<ROOT::Math::PxPyPzMVector>& mom)
{
  std::vector<ROOT::Math::PxPyPzEVector> momenta{mom.size()};
  std::transform(mom.begin(), mom.end(), momenta.begin(), [](const auto& part) {
    return ROOT::Math::PxPyPzEVector{part.Px(), part.Py(), part.Pz(), part.energy()};
  });
  return momenta;
}

// Momentum sorting bool
bool sort_mom_bool(ROOT::Math::PxPyPzEVector &mom1, ROOT::Math::PxPyPzEVector &mom2)
{
  return  mom1.energy() > mom2.energy(); 
}

// Momentunm sorting function
inline auto sort_momenta(const std::vector<ROOT::Math::PxPyPzEVector>& mom)
{
  std::vector <ROOT::Math::PxPyPzEVector> sort_mom = mom;
  sort(sort_mom.begin(), sort_mom.end(), sort_mom_bool);
  return sort_mom;
}

// Q2 calculation from 4 Vector
inline auto Q2(const std::vector<ROOT::Math::PxPyPzEVector>& mom)
{
  std::vector<double> Q2Vec(mom.size() );
  ROOT::Math::PxPyPzEVector beamMom = {0, 0, 18, 18};
  std::transform(mom.begin(), mom.end(), Q2Vec.begin(), [beamMom](const auto& part) {
    return -(part - beamMom).M2();
  });
  return Q2Vec;
}

// Difference between two 4 Vectors
inline auto sub(const std::vector<ROOT::Math::PxPyPzEVector>& mom1, const std::vector<ROOT::Math::PxPyPzEVector>& mom2)
{
  std::vector<ROOT::Math::PxPyPzEVector> sub(mom1.size() );
  for (int i = 0; i < sub.size(); i++)
  {
    sub[i] = mom1[i] - mom2[i];
  }
  return sub;
}

// Multiplies a double by a gaussian distributed number 
inline auto randomize(const std::vector<double>& doubleVec)
{
  std::vector<double> outVec(doubleVec.size() );
  TRandom3 rand;
  std::transform(doubleVec.begin(), doubleVec.end(), outVec.begin(), [&rand](const auto& indouble) {
    return indouble * rand.Gaus(1.0, 0.2);
  });
  return outVec;
}

//Simulation functions
/*
bool mom_sort_sim(dd4pod::Geant4ParticleData& part1, dd4pod::Geant4ParticleData& part2)
{
  return (part1.psx*part1.psx + part1.psy*part1.psy + part1.psz*part1.psz > 
          part2.psx*part2.psx + part2.psy*part2.psy + part2.psz*part2.psz);
}

inline auto momenta_from_sim(const std::vector<dd4pod::Geant4ParticleData>& parts)
{
  std::vector<dd4pod::Geant4ParticleData> sort_parts = parts;
  sort(sort_parts.begin(), sort_parts.end(), mom_sort_sim);
  return sort_parts;
}

inline auto Q2_from_sim(const std::vector<dd4pod::Geant4ParticleData>& parts)
{
  std::vector<double> Q2Vec(parts.size() );
  double beamEnergy = 18;
  std::transform(parts.begin(), parts.end(), Q2Vec.begin(), [beamEnergy](const auto& part) {
    double energy = sqrt(part.psx*part.psx + part.psy*part.psy + part.psz*part.psz + part.mass*part.mass);
    double q2 = pow(beamEnergy - energy, 2.0) - part.psx*part.psx - part.psy*part.psy - pow(part.psz - beamEnergy, 2.0);
    return -q2;
  });
  return Q2Vec;
}

inline auto elec_PID_sim(const std::vector<dd4pod::Geant4ParticleData>& parts)
{
  std::vector<dd4pod::Geant4ParticleData> electrons;
  for (auto part : parts)
  {
    if (part.pdgID == 11){electrons.push_back(part);}
  }
  return electrons;
}
*/


int dis_electrons(const std::string& config_name)
{
  // read our configuration
  std::ifstream  config_file{config_name};
  nlohmann::json config;
  config_file >> config;

  const std::string rec_file      = config["rec_file"];
  const std::string detector      = config["detector"];
  std::string       output_prefix = config["output_prefix"];
  const std::string test_tag      = config["test_tag"];

  fmt::print(fmt::emphasis::bold | fg(fmt::color::forest_green),
             "Running DIS electron analysis...\n");
  fmt::print(" - Detector package: {}\n", detector);
  fmt::print(" - input file: {}\n", rec_file);
  fmt::print(" - output prefix: {}\n", output_prefix);
  fmt::print(" - test tag: {}\n", test_tag);

  // create our test definition
  // test_tag
  common_bench::Test dis_Q2_resolution{
      {{"name", fmt::format("{}_Q2_resolution", test_tag)},
       {"title", "DIS Q2 resolution"},
       {"description",
        fmt::format("DIS Q2 resolution with {}, estimated using a Gaussian fit.", detector)},
       {"quantity", "resolution (in %)"},
       {"target", "0.1"}}};

  // Run this in multi-threaded mode if desired
  //ROOT::EnableImplicitMT(kNumThreads);

  //Particle number enumeration
  enum sidis_particle_ID
  {
    electron = 11,
    pi_0     = 111,
    pi_plus  = 211,
    pi_minus = -211,
    k_0      = 311,
    k_plus   = 321,
    k_minus  = -321,
    proton   = 2212,
    neutron  = 2112
  };


  const double electron_mass = util::get_pdg_mass("electron");

  // Ensure our output prefix always ends on a dot, a slash or a dash
  // Necessary when generating output plots
  if (output_prefix.back() != '.' && output_prefix.back() != '/' && output_prefix.back() != '-') {
    output_prefix += "-";
  }

  ROOT::RDataFrame d("events", rec_file);

  // utility lambda functions to bind the reconstructed particle type
  // (as we have no PID yet)
  auto momenta_from_tracking =
      [electron_mass](const std::vector<eic::TrackParametersData>& tracks) {
        return util::momenta_from_tracking(tracks, electron_mass);
      };

/*
  //Old dataframe
  auto d0 = d.Define("p_rec", momenta_from_tracking, {"outputTrackParameters"})
                .Define("N", "p_rec.size()")
                .Define("p_sim", util::momenta_from_simulation, {"mcparticles2"})
                .Define("mom_sim", util::mom, {"p_sim"})
                .Define("mom_rec", util::mom, {"p_rec"});
*/

  auto d0 = d.Define("p_recon", momenta_from_reconstruction, {"DummyReconstructedParticles"})
                .Define("p_recon_sort", sort_momenta, {"p_recon"})
                .Define("Q2_recon", Q2, {"p_recon_sort"})
                .Define("Q2_recon_rand", randomize, {"Q2_recon"})
                .Define("elec_Q2_recon_rand", "Q2_recon_rand[0]")
                .Define("p_sim_M", util::momenta_from_simulation, {"mcparticles2"})
                .Define("p_sim", convertMtoE, {"p_sim_M"})
                .Define("p_sim_sort", sort_momenta, {"p_sim"})
                .Define("Q2_sim", Q2, {"p_sim_sort"})
                .Define("elec_Q2_sim", "Q2_sim[0]")
                .Define("Q2_diff", "(elec_Q2_recon_rand - elec_Q2_sim)/elec_Q2_sim")
                .Define("p_diff", sub, {"p_recon","p_sim"});
                /*
                .Define("electrons_sim", elec_PID_sim, {"sorted_sim"})
                .Define("Q2_sim_elec_pid", Q2_from_sim, {"electrons_sim"})
                .Define("elec_Q2_sim_pid", "Q2_sim_elec_pid[0]");
                */
  //Testing script
/*
  auto dis = d0.Display({"p_diff"});
  //dis -> Print();
  cout << *d0.Max<double>("elec_Q2_recon_rand") << " " << *d0.Min<double>("elec_Q2_recon_rand") << endl;
  cout << *d0.Max<double>("elec_Q2_sim") << " " << *d0.Min<double>("elec_Q2_sim") << endl;
/**/
  //cout << *d0.Count() << endl;
  //Momentum
  //auto h_mom_sim = d0.Histo1D({"h_mom_sim", "; GeV; counts", 100, 0, 50}, "mom_sim");
  //auto h_mom_rec = d0.Histo1D({"h_mom_rec", "; GeV; counts", 100, 0, 50}, "mom_rec");
  //Q2
  auto h_Q2_sim = d0.Histo1D({"h_Q2_sim", "; GeV; counts", 100, -5, 25}, "elec_Q2_sim");
  auto h_Q2_rec = d0.Histo1D({"h_Q2_rec", "; GeV; counts", 100, -5, 25}, "elec_Q2_recon_rand");
  auto h_Q2_res = d0.Histo1D({"h_Q2_res", ";    ; counts", 100, -10, 10}, "Q2_diff");
/*
  TH1D *h_Q2_res = (TH1D *)h_Q2_sim -> Clone();
  TH1D *h_Q2_rec_copy = (TH1D *)h_Q2_rec -> Clone();
  h_Q2_res -> Scale(1.0 / h_Q2_res -> Integral() );
  h_Q2_res -> Add(h_Q2_rec_copy, -1.0 / h_Q2_rec_copy -> Integral() );
 */
  TFitResultPtr f1  = h_Q2_res -> Fit("gaus", "S");
  f1 -> Print("V");
/*
  printf("chisq %f A %f mean %f sigma %f \n", f1 -> Chi2(), 
                                              f1 -> GetParameter(0), 
                                              f1 -> GetParameter(1),
                                              f1 -> GetParameter(2));
*/

  
  auto c = new TCanvas();

  // Plot our histograms.
  // TODO: to start I'm explicitly plotting the histograms, but want to
  // factorize out the plotting code moving forward.
  {
    TCanvas c{"canvas", "canvas", 1200, 1200};
    c.cd();
    // gPad->SetLogx(false);
    gPad->SetLogy(true);
    //auto& h1 = *h_mom_sim;
    //auto& h2 = *h_mom_rec;
    auto& h1 = *h_Q2_sim;
    auto& h2 = *h_Q2_rec;
    // histogram style
    h1.SetLineColor(plot::kMpBlue);
    h1.SetLineWidth(2);
    h2.SetLineColor(plot::kMpOrange);
    h2.SetLineWidth(2);
    // axes
    h1.GetXaxis()->CenterTitle();
    h1.GetYaxis()->CenterTitle();
    // draw everything
    h1.DrawClone("hist");
    h2.DrawClone("hist same");
    // FIXME hardcoded beam configuration
    plot::draw_label(18, 275, detector);
    TText* tptr1;
    auto   t1 = new TPaveText(.6, .8417, .9, .925, "NB NDC");
    t1->SetFillColorAlpha(kWhite, 0);
    t1->SetTextFont(43);
    t1->SetTextSize(25);
    tptr1 = t1->AddText("simulated");
    tptr1->SetTextColor(plot::kMpBlue);
    tptr1 = t1->AddText("reconstructed");
    tptr1->SetTextColor(plot::kMpOrange);
    t1->Draw();

    c.Print(fmt::format("{}momentum.png", output_prefix).c_str());
  }
  common_bench::write_test({dis_Q2_resolution}, fmt::format("{}dis_electrons.json", output_prefix));

  return 0;
}
