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
  const int ebeam                 = config["ebeam"];
  const int pbeam                 = config["pbeam"];

  fmt::print(fmt::emphasis::bold | fg(fmt::color::forest_green),
             "Running DIS electron analysis...\n");
  fmt::print(" - Detector package: {}\n", detector);
  fmt::print(" - input file: {}\n", rec_file);
  fmt::print(" - output prefix: {}\n", output_prefix);
  fmt::print(" - test tag: {}\n", test_tag);
  fmt::print(" - ebeam: {}\n", ebeam);
  fmt::print(" - pbeam: {}\n", pbeam);

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
             .Define("Q2_el", "InclusiveKinematicsElectron.Q2")
             .Define("Q2_jb", "InclusiveKinematicsJB.Q2")
             .Define("Q2_da", "InclusiveKinematicsDA.Q2")
             .Define("Q2_sigma", "InclusiveKinematicsSigma.Q2")
             .Define("Q2_esigma", "InclusiveKinematicseSigma.Q2")
             .Define("Q2_el_res", combinatorial_diff_ratio, {"Q2_sim", "Q2_el"})
             .Define("Q2_jb_res", combinatorial_diff_ratio, {"Q2_sim", "Q2_jb"})
             .Define("Q2_da_res", combinatorial_diff_ratio, {"Q2_sim", "Q2_da"})
             .Define("Q2_sigma_res", combinatorial_diff_ratio, {"Q2_sim", "Q2_sigma"})
             .Define("Q2_esigma_res", combinatorial_diff_ratio, {"Q2_sim", "Q2_esigma"})
             .Define("x_sim", "InclusiveKinematicsTruth.x")
             .Define("x_el", "InclusiveKinematicsElectron.x")
             .Define("x_jb", "InclusiveKinematicsJB.x")
             .Define("x_da", "InclusiveKinematicsDA.x")
             .Define("x_sigma", "InclusiveKinematicsSigma.x")
             .Define("x_esigma", "InclusiveKinematicseSigma.x")
             .Define("x_el_res", combinatorial_diff_ratio, {"x_sim", "x_el"})
             .Define("x_jb_res", combinatorial_diff_ratio, {"x_sim", "x_jb"})
             .Define("x_da_res", combinatorial_diff_ratio, {"x_sim", "x_da"})
             .Define("x_sigma_res", combinatorial_diff_ratio, {"x_sim", "x_sigma"})
             .Define("x_esigma_res", combinatorial_diff_ratio, {"x_sim", "x_esigma"})
             ;

  //Q2
  auto h_Q2_sim = d0.Histo1D({"h_Q2_sim", "; GeV^2; counts", 100, -5, 25}, "Q2_sim");
  auto h_Q2_el = d0.Histo1D({"h_Q2_el", "; GeV^2; counts", 100, -5, 25}, "Q2_el");
  auto h_Q2_jb = d0.Histo1D({"h_Q2_jb", "; GeV^2; counts", 100, -5, 25}, "Q2_jb");
  auto h_Q2_da = d0.Histo1D({"h_Q2_da", "; GeV^2; counts", 100, -5, 25}, "Q2_da");
  auto h_Q2_sigma = d0.Histo1D({"h_Q2_sigma", "; GeV^2; counts", 100, -5, 25}, "Q2_sigma");
  auto h_Q2_esigma = d0.Histo1D({"h_Q2_esigma", "; GeV^2; counts", 100, -5, 25}, "Q2_esigma");
  auto h_Q2_el_res = d0.Histo1D({"h_Q2_el_res", ";      ; counts", 100, -1,  1}, "Q2_el_res");
  auto h_Q2_jb_res = d0.Histo1D({"h_Q2_jb_res", ";      ; counts", 100, -1,  1}, "Q2_jb_res");
  auto h_Q2_da_res = d0.Histo1D({"h_Q2_da_res", ";      ; counts", 100, -1,  1}, "Q2_da_res");
  auto h_Q2_sigma_res = d0.Histo1D({"h_Q2_sigma_res", ";      ; counts", 100, -1,  1}, "Q2_sigma_res");
  auto h_Q2_esigma_res = d0.Histo1D({"h_Q2_esigma_res", ";      ; counts", 100, -1,  1}, "Q2_esigma_res");
  //x
  auto h_x_sim = d0.Histo1D({"h_x_sim", "; ; counts", 100, 0, +1}, "x_sim");
  auto h_x_el = d0.Histo1D({"h_x_el", "; ; counts", 100, 0, +1}, "x_el");
  auto h_x_jb = d0.Histo1D({"h_x_jb", "; ; counts", 100, 0, +1}, "x_jb");
  auto h_x_da = d0.Histo1D({"h_x_da", "; ; counts", 100, 0, +1}, "x_da");
  auto h_x_sigma = d0.Histo1D({"h_x_sigma", "; ; counts", 100, 0, +1}, "x_sigma");
  auto h_x_esigma = d0.Histo1D({"h_x_esigma", "; ; counts", 100, 0, +1}, "x_esigma");
  auto h_x_el_res = d0.Histo1D({"h_x_el_res", "; ; counts", 100, -1, 1}, "x_el_res");
  auto h_x_jb_res = d0.Histo1D({"h_x_jb_res", "; ; counts", 100, -1, 1}, "x_jb_res");
  auto h_x_da_res = d0.Histo1D({"h_x_da_res", "; ; counts", 100, -1, 1}, "x_da_res");
  auto h_x_sigma_res = d0.Histo1D({"h_x_sigma_res", "; ; counts", 100, -1, 1}, "x_sigma_res");
  auto h_x_esigma_res = d0.Histo1D({"h_x_esigma_res", "; ; counts", 100, -1, 1}, "x_esigma_res");

  TFitResultPtr f_Q2_el_res = h_Q2_el_res->Fit("gaus", "S");
  if (f_Q2_el_res == 0) f_Q2_el_res->Print("V");
  TFitResultPtr f_x_el_res = h_x_el_res->Fit("gaus", "S");
  if (f_x_el_res == 0) f_x_el_res->Print("V");

  TFitResultPtr f_Q2_jb_res = h_Q2_jb_res->Fit("gaus", "S");
  if (f_Q2_jb_res == 0) f_Q2_jb_res->Print("V");
  TFitResultPtr f_x_jb_res = h_x_jb_res->Fit("gaus", "S");
  if (f_x_jb_res == 0) f_x_jb_res->Print("V");

  TFitResultPtr f_Q2_da_res = h_Q2_da_res->Fit("gaus", "S");
  if (f_Q2_da_res == 0) f_Q2_da_res->Print("V");
  TFitResultPtr f_x_da_res = h_x_da_res->Fit("gaus", "S");
  if (f_x_da_res == 0) f_x_da_res->Print("V");

  TFitResultPtr f_Q2_sigma_res = h_Q2_sigma_res->Fit("gaus", "S");
  if (f_Q2_sigma_res == 0) f_Q2_sigma_res->Print("V");
  TFitResultPtr f_x_sigma_res = h_x_sigma_res->Fit("gaus", "S");
  if (f_x_sigma_res == 0) f_x_sigma_res->Print("V");

  TFitResultPtr f_Q2_esigma_res = h_Q2_esigma_res->Fit("gaus", "S");
  if (f_Q2_esigma_res == 0) f_Q2_esigma_res->Print("V");
  TFitResultPtr f_x_esigma_res = h_x_esigma_res->Fit("gaus", "S");
  if (f_x_esigma_res == 0) f_x_esigma_res->Print("V");

  // Print summary
  fmt::print(fmt::emphasis::bold | fg(fmt::color::forest_green),
             "Inclusive kinematics summary:\n");
  fmt::print("Q2 resolution:\n");
  if (f_Q2_el_res == 0) {
    fmt::print(" - electron: {} +/- {}\n",
      f_Q2_el_res->Parameter(1), f_Q2_el_res->Error(1));
  } else {
    fmt::print("Q2 electron fit failed\n");
    return 1;
  }
  if (f_Q2_sigma_res == 0) {
    fmt::print(" - sigma:    {} +/- {}\n",
      f_Q2_sigma_res->Parameter(1), f_Q2_sigma_res->Error(1));
  } else {
    fmt::print("Q2 sigma fit failed\n");
    return 1;
  }
  if (f_Q2_esigma_res == 0) {
    fmt::print(" - esigma:   {} +/- {}\n",
      f_Q2_esigma_res->Parameter(1), f_Q2_esigma_res->Error(1));
  } else {
    fmt::print("Q2 esigma fit failed\n");
    return 1;
  }
  if (f_Q2_jb_res == 0) {
    fmt::print(" - JB:       {} +/- {}\n",
      f_Q2_jb_res->Parameter(1), f_Q2_jb_res->Error(1));
  } else {
    fmt::print("Q2 JB fit failed (FIXME: allowed to fail)\n");
    //return 1;
  }
  if (f_Q2_da_res == 0) {
    fmt::print(" - DA:       {} +/- {}\n",
      f_Q2_da_res->Parameter(1), f_Q2_da_res->Error(1));
  } else {
    fmt::print("Q2 DA fit failed\n");
    return 1;
  }
  fmt::print("x resolution:\n");
  if (f_x_el_res == 0) {
    fmt::print(" - electron: {} +/- {}\n",
      f_x_el_res->Parameter(1), f_x_el_res->Error(1));
  } else {
    fmt::print("x electron fit failed\n");
    return 1;
  }
  if (f_x_sigma_res == 0) {
    fmt::print(" - sigma:    {} +/- {}\n",
      f_x_sigma_res->Parameter(1), f_x_sigma_res->Error(1));
  } else {
    fmt::print("x sigma fit failed\n");
    return 1;
  }
  if (f_x_esigma_res == 0) {
    fmt::print(" - esigma:   {} +/- {}\n",
      f_x_esigma_res->Parameter(1), f_x_esigma_res->Error(1));
  } else {
    fmt::print("x esigma fit failed\n");
    return 1;
  }
  if (f_x_jb_res == 0) {
    fmt::print(" - JB:       {} +/- {}\n",
      f_x_jb_res->Parameter(1), f_x_jb_res->Error(1));
  } else {
    fmt::print("x JB fit failed (FIXME: allowed to fail)\n");
    //return 1;
  }
  if (f_x_da_res == 0) {
    fmt::print(" - DA:       {} +/- {}\n",
      f_x_da_res->Parameter(1), f_x_da_res->Error(1));
  } else {
    fmt::print("x DA fit failed\n");
    return 1;
  }

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
    auto& h2 = *h_Q2_el;
    auto& h3 = *h_Q2_jb;
    auto& h4 = *h_Q2_da;
    auto& h5 = *h_Q2_sigma;
    auto& h6 = *h_Q2_esigma;
    // histogram style
    h1.SetLineColor(common_bench::plot::kMpBlue);
    h1.SetLineWidth(2);
    h2.SetLineColor(common_bench::plot::kMpOrange);
    h2.SetLineWidth(2);
    h3.SetLineColor(common_bench::plot::kMpRed);
    h3.SetLineWidth(2);
    h4.SetLineColor(common_bench::plot::kMpGreen);
    h4.SetLineWidth(2);
    h5.SetLineColor(common_bench::plot::kMpMoss);
    h5.SetLineWidth(2);
    h6.SetLineColor(common_bench::plot::kMpCyan);
    h6.SetLineWidth(2);
    // axes
    h1.GetXaxis()->CenterTitle();
    h1.GetYaxis()->CenterTitle();
    // draw everything
    h1.DrawClone("hist");
    h2.DrawClone("hist same");
    h3.DrawClone("hist same");
    h4.DrawClone("hist same");
    h5.DrawClone("hist same");
    h6.DrawClone("hist same");
    // legend
    common_bench::plot::draw_label(ebeam, pbeam, detector);
    TText* tptr1;
    TPaveText t1(.6, .8417, .9, .925, "NB NDC");
    t1.SetFillColorAlpha(kWhite, 0);
    t1.SetTextFont(43);
    t1.SetTextSize(25);
    tptr1 = t1.AddText("simulated");
    tptr1->SetTextColor(common_bench::plot::kMpBlue);
    tptr1 = t1.AddText("e method");
    tptr1->SetTextColor(common_bench::plot::kMpOrange);
    tptr1 = t1.AddText("JB method");
    tptr1->SetTextColor(common_bench::plot::kMpRed);
    tptr1 = t1.AddText("DA method");
    tptr1->SetTextColor(common_bench::plot::kMpGreen);
    tptr1 = t1.AddText("#Sigma method");
    tptr1->SetTextColor(common_bench::plot::kMpMoss);
    tptr1 = t1.AddText("e#Sigma method");
    tptr1->SetTextColor(common_bench::plot::kMpCyan);
    t1.Draw();
    c.Print(fmt::format("{}_Q2.png", output_prefix).c_str());
  }

  // Q2 resolution
  {
    TCanvas c("c", "c", 1200, 1200);
    c.cd();
    gPad->SetLogx(false);
    gPad->SetLogy(true);
    auto& h1 = *h_Q2_el_res;
    auto& h2 = *h_Q2_jb_res;
    auto& h3 = *h_Q2_da_res;
    auto& h4 = *h_Q2_sigma_res;
    auto& h5 = *h_Q2_esigma_res;
    // histogram style
    h1.SetLineColor(common_bench::plot::kMpOrange);
    h1.SetLineWidth(2);
    h2.SetLineColor(common_bench::plot::kMpRed);
    h2.SetLineWidth(2);
    h3.SetLineColor(common_bench::plot::kMpGreen);
    h3.SetLineWidth(2);
    h4.SetLineColor(common_bench::plot::kMpMoss);
    h4.SetLineWidth(2);
    h5.SetLineColor(common_bench::plot::kMpCyan);
    h5.SetLineWidth(2);
    // axes
    h1.GetXaxis()->CenterTitle();
    h1.GetYaxis()->CenterTitle();
    // draw everything
    h1.DrawClone("hist");
    h2.DrawClone("hist same");
    h3.DrawClone("hist same");
    h4.DrawClone("hist same");
    h5.DrawClone("hist same");
    // legend
    common_bench::plot::draw_label(ebeam, pbeam, detector);
    TText* tptr1;
    TPaveText t1(.6, .8417, .9, .925, "NB NDC");
    t1.SetFillColorAlpha(kWhite, 0);
    t1.SetTextFont(43);
    t1.SetTextSize(25);
    tptr1 = t1.AddText("EL method");
    tptr1->SetTextColor(common_bench::plot::kMpOrange);
    tptr1 = t1.AddText("JB method");
    tptr1->SetTextColor(common_bench::plot::kMpRed);
    tptr1 = t1.AddText("DA method");
    tptr1->SetTextColor(common_bench::plot::kMpGreen);
    tptr1 = t1.AddText("#Sigma method");
    tptr1->SetTextColor(common_bench::plot::kMpMoss);
    tptr1 = t1.AddText("e#Sigma method");
    tptr1->SetTextColor(common_bench::plot::kMpCyan);
    t1.Draw();
    c.Print(fmt::format("{}_Q2_resolution.png", output_prefix).c_str());
  }

  // x comparison
  {
    TCanvas c("c", "c", 1200, 1200);
    c.cd();
    gPad->SetLogx(true);
    gPad->SetLogy(true);
    auto& h1 = *h_x_sim;
    auto& h2 = *h_x_el;
    auto& h3 = *h_x_jb;
    auto& h4 = *h_x_da;
    auto& h5 = *h_x_sigma;
    auto& h6 = *h_x_esigma;
    // histogram style
    h1.SetLineColor(common_bench::plot::kMpBlue);
    h1.SetLineWidth(2);
    h2.SetLineColor(common_bench::plot::kMpOrange);
    h2.SetLineWidth(2);
    h3.SetLineColor(common_bench::plot::kMpRed);
    h3.SetLineWidth(2);
    h4.SetLineColor(common_bench::plot::kMpGreen);
    h4.SetLineWidth(2);
    h5.SetLineColor(common_bench::plot::kMpMoss);
    h5.SetLineWidth(2);
    h6.SetLineColor(common_bench::plot::kMpCyan);
    h6.SetLineWidth(2);
    // axes
    h1.GetXaxis()->CenterTitle();
    h1.GetYaxis()->CenterTitle();
    // draw everything
    h1.DrawClone("hist");
    h2.DrawClone("hist same");
    h3.DrawClone("hist same");
    h4.DrawClone("hist same");
    h5.DrawClone("hist same");
    h6.DrawClone("hist same");
    // legend
    common_bench::plot::draw_label(ebeam, pbeam, detector);
    TText* tptr1;
    TPaveText t1(.6, .8417, .9, .925, "NB NDC");
    t1.SetFillColorAlpha(kWhite, 0);
    t1.SetTextFont(43);
    t1.SetTextSize(25);
    tptr1 = t1.AddText("simulated");
    tptr1->SetTextColor(common_bench::plot::kMpBlue);
    tptr1 = t1.AddText("EL method");
    tptr1->SetTextColor(common_bench::plot::kMpOrange);
    tptr1 = t1.AddText("JB method");
    tptr1->SetTextColor(common_bench::plot::kMpRed);
    tptr1 = t1.AddText("DA method");
    tptr1->SetTextColor(common_bench::plot::kMpGreen);
    tptr1 = t1.AddText("#Sigma method");
    tptr1->SetTextColor(common_bench::plot::kMpMoss);
    tptr1 = t1.AddText("e#Sigma method");
    tptr1->SetTextColor(common_bench::plot::kMpCyan);
    t1.Draw();
    c.Print(fmt::format("{}_x.png", output_prefix).c_str());
  }

  // x resolution
  {
    TCanvas c("c", "c", 1200, 1200);
    c.cd();
    gPad->SetLogx(false);
    gPad->SetLogy(true);
    auto& h1 = *h_x_el_res;
    auto& h2 = *h_x_jb_res;
    auto& h3 = *h_x_da_res;
    auto& h4 = *h_x_sigma_res;
    auto& h5 = *h_x_esigma_res;
    // histogram style
    h1.SetLineColor(common_bench::plot::kMpOrange);
    h1.SetLineWidth(2);
    h2.SetLineColor(common_bench::plot::kMpRed);
    h2.SetLineWidth(2);
    h3.SetLineColor(common_bench::plot::kMpGreen);
    h3.SetLineWidth(2);
    h4.SetLineColor(common_bench::plot::kMpMoss);
    h4.SetLineWidth(2);
    h5.SetLineColor(common_bench::plot::kMpCyan);
    h5.SetLineWidth(2);
    // axes
    h1.GetXaxis()->CenterTitle();
    h1.GetYaxis()->CenterTitle();
    // draw everything
    h1.DrawClone("hist");
    h2.DrawClone("hist same");
    h3.DrawClone("hist same");
    h4.DrawClone("hist same");
    h5.DrawClone("hist same");
    // legend
    common_bench::plot::draw_label(ebeam, pbeam, detector);
    TText* tptr1;
    TPaveText t1(.6, .8417, .9, .925, "NB NDC");
    t1.SetFillColorAlpha(kWhite, 0);
    t1.SetTextFont(43);
    t1.SetTextSize(25);
    tptr1 = t1.AddText("EL method");
    tptr1->SetTextColor(common_bench::plot::kMpOrange);
    tptr1 = t1.AddText("JB method");
    tptr1->SetTextColor(common_bench::plot::kMpRed);
    tptr1 = t1.AddText("DA method");
    tptr1->SetTextColor(common_bench::plot::kMpGreen);
    tptr1 = t1.AddText("#Sigma method");
    tptr1->SetTextColor(common_bench::plot::kMpMoss);
    tptr1 = t1.AddText("e#Sigma method");
    tptr1->SetTextColor(common_bench::plot::kMpCyan);
    t1.Draw();
    c.Print(fmt::format("{}_x_resolution.png", output_prefix).c_str());
  }

  common_bench::write_test({dis_Q2_resolution}, fmt::format("{}dis_electrons.json", output_prefix));

  return 0;
}
