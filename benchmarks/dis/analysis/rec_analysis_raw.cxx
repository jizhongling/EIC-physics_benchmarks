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
#include "eicd/RawCalorimeterHitData.h"

int rec_analysis_raw(const std::string& config_name)
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

  auto d0 = d.Define("n_EcalEndcapPRawHits",       "EcalEndcapPRawHits.size()")
             .Define("n_EcalBarrelImagingRawHits", "EcalBarrelImagingRawHits.size()")
             .Define("n_EcalBarrelScFiRawHits",    "EcalBarrelScFiRawHits.size()")
             .Define("n_EcalEndcapNRawHits",       "EcalEndcapNRawHits.size()")
             .Define("n_HcalEndcapPRawHits",       "HcalEndcapPRawHits.size()")
             .Define("n_HcalBarrelRawHits",        "HcalBarrelRawHits.size()")
             .Define("n_HcalEndcapNRawHits",       "HcalEndcapNRawHits.size()")
             ;

  // Ecal
  auto h_n_EcalEndcapPRawHits = d0.Histo1D({"h_n_EcalEndcapPRawHits", "; hits; counts", 100, 0, 1000}, "n_EcalEndcapPRawHits");
  auto h_n_EcalBarrelImagingRawHits = d0.Histo1D({"h_n_EcalBarrelImagingRawHits", "; hits; counts", 100, 0, 1000}, "n_EcalBarrelImagingRawHits");
  auto h_n_EcalBarrelScFiRawHits = d0.Histo1D({"h_n_EcalBarrelScFiRawHits", "; hits; counts", 100, 0, 10000}, "n_EcalBarrelScFiRawHits");
  auto h_n_EcalEndcapNRawHits = d0.Histo1D({"h_n_EcalEndcapNRawHits", "; hits; counts", 100, 0, 1000}, "n_EcalEndcapNRawHits");
  auto h_adc_EcalEndcapPRawHits = d0.Histo1D({"h_adc_EcalEndcapPRawHits", "; amplitude; counts", 1024, 0, 32768}, "EcalEndcapPRawHits.amplitude");
  auto h_adc_EcalBarrelImagingRawHits = d0.Histo1D({"h_adc_EcalBarrelImagingRawHits", "; amplitude; counts", 1024, 0, 8192}, "EcalBarrelImagingRawHits.amplitude");
  auto h_adc_EcalBarrelScFiRawHits = d0.Histo1D({"h_adc_EcalBarrelScFiRawHits", "; amplitude; counts", 1024, 0, 32768}, "EcalBarrelScFiRawHits.amplitude");
  auto h_adc_EcalEndcapNRawHits = d0.Histo1D({"h_adc_EcalEndcapNRawHits", "; amplitude; counts", 1024, 0, 32768}, "EcalEndcapNRawHits.amplitude");
  auto h_tdc_EcalEndcapPRawHits = d0.Histo1D({"h_tdc_EcalEndcapPRawHits", "; TDC channel; counts", 1024, 0, 32768}, "EcalEndcapPRawHits.time");
  auto h_tdc_EcalBarrelImagingRawHits = d0.Histo1D({"h_tdc_EcalBarrelImagingRawHits", "; TDC channel; counts", 1024, 0, 32768}, "EcalBarrelImagingRawHits.time");
  auto h_tdc_EcalBarrelScFiRawHits = d0.Histo1D({"h_tdc_EcalBarrelScFiRawHits", "; TDC channel; counts", 1024, 0, 32768}, "EcalBarrelScFiRawHits.time");
  auto h_tdc_EcalEndcapNRawHits = d0.Histo1D({"h_tdc_EcalEndcapNRawHits", "; TDC channel; counts", 1024, 0, 32768}, "EcalEndcapNRawHits.time");
  // Hcal
  auto h_n_HcalEndcapPRawHits = d0.Histo1D({"h_n_HcalEndcapPRawHits", "; hits; counts", 100, 0, 1000}, "n_HcalEndcapPRawHits");
  auto h_n_HcalBarrelRawHits  = d0.Histo1D({"h_n_HcalBarrelRawHits",  "; hits; counts", 100, 0, 1000}, "n_HcalBarrelRawHits");
  auto h_n_HcalEndcapNRawHits = d0.Histo1D({"h_n_HcalEndcapNRawHits", "; hits; counts", 100, 0, 1000}, "n_HcalEndcapNRawHits");
  auto h_adc_HcalEndcapPRawHits = d0.Histo1D({"h_adc_HcalEndcapPRawHits", "; hits; counts", 1024, 0, 32768}, "HcalEndcapPRawHits.amplitude");
  auto h_adc_HcalBarrelRawHits  = d0.Histo1D({"h_adc_HcalBarrelRawHits",  "; hits; counts", 1024, 0, 32768}, "HcalBarrelRawHits.amplitude");
  auto h_adc_HcalEndcapNRawHits = d0.Histo1D({"h_adc_HcalEndcapNRawHits", "; hits; counts", 1024, 0, 32768}, "HcalEndcapNRawHits.amplitude");
  auto h_tdc_HcalEndcapPRawHits = d0.Histo1D({"h_tdc_HcalEndcapPRawHits", "; TDC channel; counts", 1024, 0, 32768}, "HcalEndcapPRawHits.time");
  auto h_tdc_HcalBarrelRawHits  = d0.Histo1D({"h_tdc_HcalBarrelRawHits",  "; TDC channel; counts", 1024, 0, 32768}, "HcalBarrelRawHits.time");
  auto h_tdc_HcalEndcapNRawHits = d0.Histo1D({"h_tdc_HcalEndcapNRawHits", "; TDC channel; counts", 1024, 0, 32768}, "HcalEndcapNRawHits.time");

  // Ecal nhits
  {
    TCanvas c("c", "c", 1200, 1200);
    c.Divide(2,2);

    c.cd(1);
    gPad->SetLogy(true);
    auto& h1 = *h_n_EcalEndcapPRawHits;
    // histogram style
    h1.SetLineColor(common_bench::plot::kMpBlue);
    h1.SetLineWidth(2);
    // axes
    h1.GetXaxis()->CenterTitle();
    h1.GetYaxis()->CenterTitle();
    // draw everything
    h1.DrawClone("hist");

    c.cd(2);
    gPad->SetLogy(true);
    auto& h2 = *h_n_EcalEndcapNRawHits;
    // histogram style
    h2.SetLineColor(common_bench::plot::kMpBlue);
    h2.SetLineWidth(2);
    // axes
    h2.GetXaxis()->CenterTitle();
    h2.GetYaxis()->CenterTitle();
    // draw everything
    h2.DrawClone("hist");

    c.cd(3);
    gPad->SetLogy(true);
    auto& h3 = *h_n_EcalBarrelImagingRawHits;
    // histogram style
    h3.SetLineColor(common_bench::plot::kMpBlue);
    h3.SetLineWidth(2);
    // axes
    h3.GetXaxis()->CenterTitle();
    h3.GetYaxis()->CenterTitle();
    // draw everything
    h3.DrawClone("hist");

    c.cd(4);
    gPad->SetLogy(true);
    auto& h4 = *h_n_EcalBarrelScFiRawHits;
    // histogram style
    h4.SetLineColor(common_bench::plot::kMpBlue);
    h4.SetLineWidth(2);
    // axes
    h4.GetXaxis()->CenterTitle();
    h4.GetYaxis()->CenterTitle();
    // draw everything
    h4.DrawClone("hist");

    // FIXME hardcoded beam configuration
    common_bench::plot::draw_label(18, 275, detector);
    TText* tptr1;
    TPaveText t1(.6, .8417, .9, .925, "NB NDC");
    t1.SetFillColorAlpha(kWhite, 0);
    t1.SetTextFont(43);
    t1.SetTextSize(25);
    tptr1 = t1.AddText("simulated");
    tptr1->SetTextColor(common_bench::plot::kMpBlue);
    t1.Draw();

    c.Print(fmt::format("{}EcalRawHits_n.png", output_prefix).c_str());
  }

  // Ecal adc
  {
    TCanvas c("c", "c", 1200, 1200);
    c.Divide(2,2);

    c.cd(1);
    gPad->SetLogy(true);
    auto& h1 = *h_adc_EcalEndcapPRawHits;
    // histogram style
    h1.SetLineColor(common_bench::plot::kMpBlue);
    h1.SetLineWidth(2);
    // axes
    h1.GetXaxis()->CenterTitle();
    h1.GetYaxis()->CenterTitle();
    // draw everything
    h1.DrawClone("hist");

    c.cd(2);
    gPad->SetLogy(true);
    auto& h2 = *h_adc_EcalEndcapNRawHits;
    // histogram style
    h2.SetLineColor(common_bench::plot::kMpBlue);
    h2.SetLineWidth(2);
    // axes
    h2.GetXaxis()->CenterTitle();
    h2.GetYaxis()->CenterTitle();
    // draw everything
    h2.DrawClone("hist");

    c.cd(3);
    gPad->SetLogy(true);
    auto& h3 = *h_adc_EcalBarrelImagingRawHits;
    // histogram style
    h3.SetLineColor(common_bench::plot::kMpBlue);
    h3.SetLineWidth(2);
    // axes
    h3.GetXaxis()->CenterTitle();
    h3.GetYaxis()->CenterTitle();
    // draw everything
    h3.DrawClone("hist");

    c.cd(4);
    gPad->SetLogy(true);
    auto& h4 = *h_adc_EcalBarrelScFiRawHits;
    // histogram style
    h4.SetLineColor(common_bench::plot::kMpBlue);
    h4.SetLineWidth(2);
    // axes
    h4.GetXaxis()->CenterTitle();
    h4.GetYaxis()->CenterTitle();
    // draw everything
    h4.DrawClone("hist");

    // FIXME hardcoded beam configuration
    common_bench::plot::draw_label(18, 275, detector);
    TText* tptr1;
    TPaveText t1(.6, .8417, .9, .925, "NB NDC");
    t1.SetFillColorAlpha(kWhite, 0);
    t1.SetTextFont(43);
    t1.SetTextSize(25);
    tptr1 = t1.AddText("simulated");
    tptr1->SetTextColor(common_bench::plot::kMpBlue);
    t1.Draw();

    c.Print(fmt::format("{}EcalRawHits_adc.png", output_prefix).c_str());
  }


  // Ecal tdc
  {
    TCanvas c("c", "c", 1200, 1200);
    c.Divide(2,2);

    c.cd(1);
    gPad->SetLogy(true);
    auto& h1 = *h_tdc_EcalEndcapPRawHits;
    // histogram style
    h1.SetLineColor(common_bench::plot::kMpBlue);
    h1.SetLineWidth(2);
    // axes
    h1.GetXaxis()->CenterTitle();
    h1.GetYaxis()->CenterTitle();
    // draw everything
    h1.DrawClone("hist");

    c.cd(2);
    gPad->SetLogy(true);
    auto& h2 = *h_tdc_EcalEndcapNRawHits;
    // histogram style
    h2.SetLineColor(common_bench::plot::kMpBlue);
    h2.SetLineWidth(2);
    // axes
    h2.GetXaxis()->CenterTitle();
    h2.GetYaxis()->CenterTitle();
    // draw everything
    h2.DrawClone("hist");

    c.cd(3);
    gPad->SetLogy(true);
    auto& h3 = *h_tdc_EcalBarrelImagingRawHits;
    // histogram style
    h3.SetLineColor(common_bench::plot::kMpBlue);
    h3.SetLineWidth(2);
    // axes
    h3.GetXaxis()->CenterTitle();
    h3.GetYaxis()->CenterTitle();
    // draw everything
    h3.DrawClone("hist");

    c.cd(4);
    gPad->SetLogy(true);
    auto& h4 = *h_tdc_EcalBarrelScFiRawHits;
    // histogram style
    h4.SetLineColor(common_bench::plot::kMpBlue);
    h4.SetLineWidth(2);
    // axes
    h4.GetXaxis()->CenterTitle();
    h4.GetYaxis()->CenterTitle();
    // draw everything
    h4.DrawClone("hist");

    // FIXME hardcoded beam configuration
    common_bench::plot::draw_label(18, 275, detector);
    TText* tptr1;
    TPaveText t1(.6, .8417, .9, .925, "NB NDC");
    t1.SetFillColorAlpha(kWhite, 0);
    t1.SetTextFont(43);
    t1.SetTextSize(25);
    tptr1 = t1.AddText("simulated");
    tptr1->SetTextColor(common_bench::plot::kMpBlue);
    t1.Draw();

    c.Print(fmt::format("{}EcalRawHits_tdc.png", output_prefix).c_str());
  }

  // Hcal nhits
  {
    TCanvas c("c", "c", 1200, 1200);
    c.Divide(2,2);

    c.cd(1);
    gPad->SetLogy(true);
    auto& h1 = *h_n_HcalEndcapPRawHits;
    // histogram style
    h1.SetLineColor(common_bench::plot::kMpBlue);
    h1.SetLineWidth(2);
    // axes
    h1.GetXaxis()->CenterTitle();
    h1.GetYaxis()->CenterTitle();
    // draw everything
    h1.DrawClone("hist");

    c.cd(2);
    gPad->SetLogy(true);
    auto& h2 = *h_n_HcalEndcapNRawHits;
    // histogram style
    h2.SetLineColor(common_bench::plot::kMpBlue);
    h2.SetLineWidth(2);
    // axes
    h2.GetXaxis()->CenterTitle();
    h2.GetYaxis()->CenterTitle();
    // draw everything
    h2.DrawClone("hist");

    c.cd(3);
    gPad->SetLogy(true);
    auto& h3 = *h_n_HcalBarrelRawHits;
    // histogram style
    h3.SetLineColor(common_bench::plot::kMpBlue);
    h3.SetLineWidth(2);
    // axes
    h3.GetXaxis()->CenterTitle();
    h3.GetYaxis()->CenterTitle();
    // draw everything
    h3.DrawClone("hist");

    // FIXME hardcoded beam configuration
    common_bench::plot::draw_label(18, 275, detector);
    TText* tptr1;
    TPaveText t1(.6, .8417, .9, .925, "NB NDC");
    t1.SetFillColorAlpha(kWhite, 0);
    t1.SetTextFont(43);
    t1.SetTextSize(25);
    tptr1 = t1.AddText("simulated");
    tptr1->SetTextColor(common_bench::plot::kMpBlue);
    t1.Draw();

    c.Print(fmt::format("{}HcalRawHits_n.png", output_prefix).c_str());
  }

  // Hcal adc
  {
    TCanvas c("c", "c", 1200, 1200);
    c.Divide(2,2);

    c.cd(1);
    gPad->SetLogy(true);
    auto& h1 = *h_adc_HcalEndcapPRawHits;
    // histogram style
    h1.SetLineColor(common_bench::plot::kMpBlue);
    h1.SetLineWidth(2);
    // axes
    h1.GetXaxis()->CenterTitle();
    h1.GetYaxis()->CenterTitle();
    // draw everything
    h1.DrawClone("hist");

    c.cd(2);
    gPad->SetLogy(true);
    auto& h2 = *h_adc_HcalEndcapNRawHits;
    // histogram style
    h2.SetLineColor(common_bench::plot::kMpBlue);
    h2.SetLineWidth(2);
    // axes
    h2.GetXaxis()->CenterTitle();
    h2.GetYaxis()->CenterTitle();
    // draw everything
    h2.DrawClone("hist");

    c.cd(3);
    gPad->SetLogy(true);
    auto& h3 = *h_adc_HcalBarrelRawHits;
    // histogram style
    h3.SetLineColor(common_bench::plot::kMpBlue);
    h3.SetLineWidth(2);
    // axes
    h3.GetXaxis()->CenterTitle();
    h3.GetYaxis()->CenterTitle();
    // draw everything
    h3.DrawClone("hist");

    // FIXME hardcoded beam configuration
    common_bench::plot::draw_label(18, 275, detector);
    TText* tptr1;
    TPaveText t1(.6, .8417, .9, .925, "NB NDC");
    t1.SetFillColorAlpha(kWhite, 0);
    t1.SetTextFont(43);
    t1.SetTextSize(25);
    tptr1 = t1.AddText("simulated");
    tptr1->SetTextColor(common_bench::plot::kMpBlue);
    t1.Draw();

    c.Print(fmt::format("{}HcalRawHits_adc.png", output_prefix).c_str());
  }

  // Hcal tdc
  {
    TCanvas c("c", "c", 1200, 1200);
    c.Divide(2,2);

    c.cd(1);
    gPad->SetLogy(true);
    auto& h1 = *h_tdc_HcalEndcapPRawHits;
    // histogram style
    h1.SetLineColor(common_bench::plot::kMpBlue);
    h1.SetLineWidth(2);
    // axes
    h1.GetXaxis()->CenterTitle();
    h1.GetYaxis()->CenterTitle();
    // draw everything
    h1.DrawClone("hist");

    c.cd(2);
    gPad->SetLogy(true);
    auto& h2 = *h_tdc_HcalEndcapNRawHits;
    // histogram style
    h2.SetLineColor(common_bench::plot::kMpBlue);
    h2.SetLineWidth(2);
    // axes
    h2.GetXaxis()->CenterTitle();
    h2.GetYaxis()->CenterTitle();
    // draw everything
    h2.DrawClone("hist");

    c.cd(3);
    gPad->SetLogy(true);
    auto& h3 = *h_tdc_HcalBarrelRawHits;
    // histogram style
    h3.SetLineColor(common_bench::plot::kMpBlue);
    h3.SetLineWidth(2);
    // axes
    h3.GetXaxis()->CenterTitle();
    h3.GetYaxis()->CenterTitle();
    // draw everything
    h3.DrawClone("hist");

    // FIXME hardcoded beam configuration
    common_bench::plot::draw_label(18, 275, detector);
    TText* tptr1;
    TPaveText t1(.6, .8417, .9, .925, "NB NDC");
    t1.SetFillColorAlpha(kWhite, 0);
    t1.SetTextFont(43);
    t1.SetTextSize(25);
    tptr1 = t1.AddText("simulated");
    tptr1->SetTextColor(common_bench::plot::kMpBlue);
    t1.Draw();

    c.Print(fmt::format("{}HcalRawHits_tdc.png", output_prefix).c_str());
  }

  auto stats_n_EcalEndcapPRawHits = d0.Stats("n_EcalEndcapPRawHits");
  auto stats_n_EcalBarrelImagingRawHits = d0.Stats("n_EcalBarrelImagingRawHits");
  auto stats_n_EcalBarrelScFiRawHits = d0.Stats("n_EcalBarrelScFiRawHits");
  auto stats_n_EcalEndcapNRawHits = d0.Stats("n_EcalEndcapNRawHits");
  auto stats_n_HcalEndcapPRawHits = d0.Stats("n_HcalEndcapPRawHits");
  auto stats_n_HcalBarrelRawHits  = d0.Stats("n_HcalBarrelRawHits");
  auto stats_n_HcalEndcapNRawHits = d0.Stats("n_HcalEndcapNRawHits");
  stats_n_EcalEndcapPRawHits->Print();
  stats_n_EcalBarrelImagingRawHits->Print();
  stats_n_EcalBarrelScFiRawHits->Print();
  stats_n_EcalEndcapNRawHits->Print();
  stats_n_HcalEndcapPRawHits->Print();
  stats_n_HcalBarrelRawHits->Print();
  stats_n_HcalEndcapNRawHits->Print();
  if (
    stats_n_EcalEndcapPRawHits->GetMean() < 0.8 ||
    stats_n_EcalBarrelImagingRawHits->GetMean() < 0.8 ||
    stats_n_EcalBarrelScFiRawHits->GetMean() < 0.8 ||
    stats_n_EcalEndcapNRawHits->GetMean() < 0.8 ||
    stats_n_HcalEndcapPRawHits->GetMean() < 0.8 ||
    stats_n_HcalBarrelRawHits->GetMean() < 0.8 ||
    stats_n_HcalEndcapNRawHits->GetMean() < 0.8
   ) {
    std::cout << "Error: too few raw hits per events " << std::endl;
    return -1;
  }

  return 0;
}
