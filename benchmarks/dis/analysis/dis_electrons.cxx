#include "common_bench/benchmark.h"
#include "common_bench/mt.h"
#include "common_bench/util.h"
#include "common_bench/plot.h"

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
#include <TCanvas.h>

#include "fmt/color.h"
#include "fmt/core.h"

#include "nlohmann/json.hpp"
#include "eicd/InclusiveKinematicsData.h"
#include "eicd/ReconstructedParticleData.h"

int dis_electrons(const std::string& config_name)
{
  // read our configuration
  std::ifstream  config_file{config_name};
  nlohmann::json config;
  config_file >> config;

  const std::string rec_file      = config["rec_file"];
  const std::string detector      = config["detector"];
  const std::string output_prefix = config["output_prefix"];
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
  ROOT::EnableImplicitMT(kNumThreads);
  ROOT::RDataFrame d("events", rec_file);

  auto combinatorial_diff_ratio = [] (
      const ROOT::VecOps::RVec<float>& v1,
      const ROOT::VecOps::RVec<float>& v2
  ) {
    std::vector<float> v;
    for (auto& i1: v1) {
      for (auto& i2: v2) {
        if (i1 != 0) {
          v.push_back((i1-i2)/i1);
        }
      }
    }
    return v;
  };

  auto d0 = d.Define("Q2_sim", "InclusiveKinematicsTruth.Q2")
             .Define("Q2_rec", "InclusiveKinematicsElectron.Q2")
             .Define("Q2_res", combinatorial_diff_ratio, {"Q2_sim", "Q2_rec"})
             .Define("x_sim", "InclusiveKinematicsTruth.x")
             .Define("x_rec", "InclusiveKinematicsElectron.x")
             .Define("x_res", combinatorial_diff_ratio, {"x_sim", "x_rec"})
             ;

  //Q2
  auto h_Q2_sim = d0.Histo1D({"h_Q2_sim", "; GeV^2; counts", 100, -5, 25}, "Q2_sim");
  auto h_Q2_rec = d0.Histo1D({"h_Q2_rec", "; GeV^2; counts", 100, -5, 25}, "Q2_rec");
  auto h_Q2_res = d0.Histo1D({"h_Q2_res", ";      ; counts", 100, -1,  1}, "Q2_res");
  //x
  auto h_x_sim = d0.Histo1D({"h_x_sim", "; ; counts", 100, 0, +1}, "x_sim");
  auto h_x_rec = d0.Histo1D({"h_x_rec", "; ; counts", 100, 0, +1}, "x_rec");
  auto h_x_res = d0.Histo1D({"h_x_res", "; ; counts", 100, -1, 1}, "x_res");

  TFitResultPtr f_Q2_res = h_Q2_res->Fit("gaus", "S");
  if (f_Q2_res == 0) f_Q2_res->Print("V");
  TFitResultPtr f_x_res = h_x_res->Fit("gaus", "S");
  if (f_x_res == 0) f_x_res->Print("V");

  // Plot our histograms.
  // TODO: to start I'm explicitly plotting the histograms, but want to
  // factorize out the plotting code moving forward.

  // Q2 comparison
  {
    TCanvas c("c", "c", 1200, 1200);
    c.cd();
    gPad->SetLogx(false);
    gPad->SetLogy(true);
    auto& h1 = *h_Q2_sim;
    auto& h2 = *h_Q2_rec;
    // histogram style
    h1.SetLineColor(common_bench::plot::kMpBlue);
    h1.SetLineWidth(2);
    h2.SetLineColor(common_bench::plot::kMpOrange);
    h2.SetLineWidth(2);
    // axes
    h1.GetXaxis()->CenterTitle();
    h1.GetYaxis()->CenterTitle();
    // draw everything
    h1.DrawClone("hist");
    h2.DrawClone("hist same");
    // FIXME hardcoded beam configuration
    common_bench::plot::draw_label(18, 275, detector);
    TText* tptr1;
    TPaveText t1(.6, .8417, .9, .925, "NB NDC");
    t1.SetFillColorAlpha(kWhite, 0);
    t1.SetTextFont(43);
    t1.SetTextSize(25);
    tptr1 = t1.AddText("simulated");
    tptr1->SetTextColor(common_bench::plot::kMpBlue);
    tptr1 = t1.AddText("reconstructed");
    tptr1->SetTextColor(common_bench::plot::kMpOrange);
    t1.Draw();
    c.Print(fmt::format("{}Q2.png", output_prefix).c_str());
  }

  // Q2 resolution
  {
    TCanvas c("c", "c", 1200, 1200);
    c.cd();
    gPad->SetLogx(false);
    gPad->SetLogy(true);
    auto& h1 = *h_Q2_res;
    // histogram style
    h1.SetLineColor(common_bench::plot::kMpBlue);
    h1.SetLineWidth(2);
    // axes
    h1.GetXaxis()->CenterTitle();
    h1.GetYaxis()->CenterTitle();
    // draw everything
    h1.DrawClone("hist");
    // FIXME hardcoded beam configuration
    common_bench::plot::draw_label(18, 275, detector);
    c.Print(fmt::format("{}Q2resolution.png", output_prefix).c_str());
  }

  // x comparison
  {
    TCanvas c("c", "c", 1200, 1200);
    c.cd();
    gPad->SetLogx(true);
    gPad->SetLogy(true);
    auto& h1 = *h_x_sim;
    auto& h2 = *h_x_rec;
    // histogram style
    h1.SetLineColor(common_bench::plot::kMpBlue);
    h1.SetLineWidth(2);
    h2.SetLineColor(common_bench::plot::kMpOrange);
    h2.SetLineWidth(2);
    // axes
    h1.GetXaxis()->CenterTitle();
    h1.GetYaxis()->CenterTitle();
    // draw everything
    h1.DrawClone("hist");
    h2.DrawClone("hist same");
    // FIXME hardcoded beam configuration
    common_bench::plot::draw_label(18, 275, detector);
    TText* tptr1;
    TPaveText t1(.6, .8417, .9, .925, "NB NDC");
    t1.SetFillColorAlpha(kWhite, 0);
    t1.SetTextFont(43);
    t1.SetTextSize(25);
    tptr1 = t1.AddText("simulated");
    tptr1->SetTextColor(common_bench::plot::kMpBlue);
    tptr1 = t1.AddText("reconstructed");
    tptr1->SetTextColor(common_bench::plot::kMpOrange);
    t1.Draw();
    c.Print(fmt::format("{}x.png", output_prefix).c_str());
  }

  // x resolution
  {
    TCanvas c("c", "c", 1200, 1200);
    c.cd();
    gPad->SetLogx(false);
    gPad->SetLogy(true);
    auto& h1 = *h_x_res;
    // histogram style
    h1.SetLineColor(common_bench::plot::kMpBlue);
    h1.SetLineWidth(2);
    // axes
    h1.GetXaxis()->CenterTitle();
    h1.GetYaxis()->CenterTitle();
    // draw everything
    h1.DrawClone("hist");
    // FIXME hardcoded beam configuration
    common_bench::plot::draw_label(18, 275, detector);
    c.Print(fmt::format("{}xresolution.png", output_prefix).c_str());
  }

  common_bench::write_test({dis_Q2_resolution}, fmt::format("{}dis_electrons.json", output_prefix));

  return 0;
}
