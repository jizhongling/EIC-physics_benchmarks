#include "dis.h"
#include "plot.h"

#include <benchmark.h>
#include <mt.h>
#include <util.h>

#include "ROOT/RDataFrame.hxx"
#include <cmath>
#include <fmt/color.h>
#include <fmt/core.h>
#include <fstream>
#include <iostream>
#include <nlohmann/json.hpp>
#include <string>
#include <vector>

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
  eic::util::Test dis_Q2_resolution{
      {{"name", fmt::format("{}_Q2_resolution", test_tag)},
       {"title", "DIS Q2 resolution"},
       {"description",
        fmt::format("DIS Q2 resolution with {}, estimated using a Gaussian fit.", detector)},
       {"quantity", "resolution (in %)"},
       {"target", "0.1"}}};

  // Run this in multi-threaded mode if desired
  ROOT::EnableImplicitMT(kNumThreads);

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

  auto d0 = d.Define("p_rec", momenta_from_tracking, {"outputTrackParameters"})
                .Define("N", "p_rec.size()")
                .Define("p_sim", util::momenta_from_simulation, {"mcparticles2"})
                .Define("mom_sim", util::mom, {"p_sim"})
                .Define("mom_rec", util::mom, {"p_rec"});

  auto h_mom_sim = d0.Histo1D({"h_mom_sim", "; GeV; counts", 100, 0, 50}, "mom_sim");
  auto h_mom_rec = d0.Histo1D({"h_mom_rec", "; GeV; counts", 100, 0, 50}, "mom_rec");

  auto c = new TCanvas();

  // Plot our histograms.
  // TODO: to start I'm explicitly plotting the histograms, but want to
  // factorize out the plotting code moving forward.
  {
    TCanvas c{"canvas", "canvas", 1200, 1200};
    c.cd();
    // gPad->SetLogx(false);
    gPad->SetLogy(true);
    auto& h1 = *h_mom_sim;
    auto& h2 = *h_mom_rec;
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
  eic::util::write_test({dis_Q2_resolution}, fmt::format("{}dis_electrons.json", output_prefix));

  return 0;
}
