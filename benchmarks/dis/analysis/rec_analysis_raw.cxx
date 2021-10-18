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

  // Ecal hits
  auto h_n_EcalEndcapPRawHits = d0.Histo1D({"h_n_EcalEndcapPRawHits", "EcalEndcapP; hits; counts", 100, 0, 1000}, "n_EcalEndcapPRawHits");
  auto h_n_EcalBarrelImagingRawHits = d0.Histo1D({"h_n_EcalBarrelImagingRawHits", "EcalBarrelImaging; hits; counts", 100, 0, 1000}, "n_EcalBarrelImagingRawHits");
  auto h_n_EcalBarrelScFiRawHits = d0.Histo1D({"h_n_EcalBarrelScFiRawHits", "EcalBarrelScFi; hits; counts", 100, 0, 10000}, "n_EcalBarrelScFiRawHits");
  auto h_n_EcalEndcapNRawHits = d0.Histo1D({"h_n_EcalEndcapNRawHits", "EcalEndcapN; hits; counts", 100, 0, 1000}, "n_EcalEndcapNRawHits");
  // Ecal stats
  auto stats_n_EcalEndcapPRawHits = d0.Stats("n_EcalEndcapPRawHits");
  auto stats_n_EcalBarrelImagingRawHits = d0.Stats("n_EcalBarrelImagingRawHits");
  auto stats_n_EcalBarrelScFiRawHits = d0.Stats("n_EcalBarrelScFiRawHits");
  auto stats_n_EcalEndcapNRawHits = d0.Stats("n_EcalEndcapNRawHits");
  // Ecal adc
  auto h_adc_EcalEndcapPRawHits = d0.Histo1D({"h_adc_EcalEndcapPRawHits", "EcalEndcapP; amplitude; counts", 1024, 0, 32768}, "EcalEndcapPRawHits.amplitude");
  auto h_adc_EcalBarrelImagingRawHits = d0.Histo1D({"h_adc_EcalBarrelImagingRawHits", "EcalBarrelImaging; amplitude; counts", 1024, 0, 8192}, "EcalBarrelImagingRawHits.amplitude");
  auto h_adc_EcalBarrelScFiRawHits = d0.Histo1D({"h_adc_EcalBarrelScFiRawHits", "EcalBarrelScFi; amplitude; counts", 1024, 0, 32768}, "EcalBarrelScFiRawHits.amplitude");
  auto h_adc_EcalEndcapNRawHits = d0.Histo1D({"h_adc_EcalEndcapNRawHits", "EcalEndcapN; amplitude; counts", 1024, 0, 32768}, "EcalEndcapNRawHits.amplitude");
  // Ecal tdc
  auto h_tdc_EcalEndcapPRawHits = d0.Histo1D({"h_tdc_EcalEndcapPRawHits", "EcalEndcapP; TDC channel; counts", 1024, 0, 32768}, "EcalEndcapPRawHits.time");
  auto h_tdc_EcalBarrelImagingRawHits = d0.Histo1D({"h_tdc_EcalBarrelImagingRawHits", "EcalBarrelImaging; TDC channel; counts", 1024, 0, 32768}, "EcalBarrelImagingRawHits.time");
  auto h_tdc_EcalBarrelScFiRawHits = d0.Histo1D({"h_tdc_EcalBarrelScFiRawHits", "EcalBarrelScFi; TDC channel; counts", 1024, 0, 32768}, "EcalBarrelScFiRawHits.time");
  auto h_tdc_EcalEndcapNRawHits = d0.Histo1D({"h_tdc_EcalEndcapNRawHits", "EcalEndcapN; TDC channel; counts", 1024, 0, 32768}, "EcalEndcapNRawHits.time");
  // Hcal hits
  auto h_n_HcalEndcapPRawHits = d0.Histo1D({"h_n_HcalEndcapPRawHits", "HcalEndcapP; hits; counts", 100, 0, 1000}, "n_HcalEndcapPRawHits");
  auto h_n_HcalBarrelRawHits  = d0.Histo1D({"h_n_HcalBarrelRawHits",  "HcalBarrel; hits; counts", 100, 0, 1000}, "n_HcalBarrelRawHits");
  auto h_n_HcalEndcapNRawHits = d0.Histo1D({"h_n_HcalEndcapNRawHits", "HcalEndcapN; hits; counts", 100, 0, 1000}, "n_HcalEndcapNRawHits");
  // Hcal stats
  auto stats_n_HcalEndcapPRawHits = d0.Stats("n_HcalEndcapPRawHits");
  auto stats_n_HcalBarrelRawHits  = d0.Stats("n_HcalBarrelRawHits");
  auto stats_n_HcalEndcapNRawHits = d0.Stats("n_HcalEndcapNRawHits");
  // Hcal adc
  auto h_adc_HcalEndcapPRawHits = d0.Histo1D({"h_adc_HcalEndcapPRawHits", "HcalEndcapP; hits; counts", 1024, 0, 32768}, "HcalEndcapPRawHits.amplitude");
  auto h_adc_HcalBarrelRawHits  = d0.Histo1D({"h_adc_HcalBarrelRawHits",  "HcalBarrel; hits; counts", 1024, 0, 32768}, "HcalBarrelRawHits.amplitude");
  auto h_adc_HcalEndcapNRawHits = d0.Histo1D({"h_adc_HcalEndcapNRawHits", "HcalEndcapN; hits; counts", 1024, 0, 32768}, "HcalEndcapNRawHits.amplitude");
  // Hcal tdc
  auto h_tdc_HcalEndcapPRawHits = d0.Histo1D({"h_tdc_HcalEndcapPRawHits", "HcalEndcapP; TDC channel; counts", 1024, 0, 32768}, "HcalEndcapPRawHits.time");
  auto h_tdc_HcalBarrelRawHits  = d0.Histo1D({"h_tdc_HcalBarrelRawHits",  "HcalBarrel; TDC channel; counts", 1024, 0, 32768}, "HcalBarrelRawHits.time");
  auto h_tdc_HcalEndcapNRawHits = d0.Histo1D({"h_tdc_HcalEndcapNRawHits", "HcalEndcapN; TDC channel; counts", 1024, 0, 32768}, "HcalEndcapNRawHits.time");

  fmt::print("EcalEndcapPRawHits:");
  stats_n_EcalEndcapPRawHits->Print();
  fmt::print("EcalBarrelImagingRawHits:");
  stats_n_EcalBarrelImagingRawHits->Print();
  fmt::print("EcalBarrelScFiRawHits:");
  stats_n_EcalBarrelScFiRawHits->Print();
  fmt::print("EcalEndcapNRawHits:");
  stats_n_EcalEndcapNRawHits->Print();
  fmt::print("HcalEndcapPRawHits:");
  stats_n_HcalEndcapPRawHits->Print();
  fmt::print("HcalBarrelRawHits:");
  stats_n_HcalBarrelRawHits->Print();
  fmt::print("HcalEndcapNRawHits:");
  stats_n_HcalEndcapNRawHits->Print();


  gStyle->SetOptTitle(kTRUE);

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
    common_bench::plot::draw_label(ebeam, pbeam, detector);

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

    c.Print(fmt::format("{}_EcalRawHits_n.png", output_prefix).c_str());
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
    common_bench::plot::draw_label(ebeam, pbeam, detector);

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

    c.Print(fmt::format("{}_EcalRawHits_adc.png", output_prefix).c_str());
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
    common_bench::plot::draw_label(ebeam, pbeam, detector);

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

    c.Print(fmt::format("{}_EcalRawHits_tdc.png", output_prefix).c_str());
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
    common_bench::plot::draw_label(ebeam, pbeam, detector);

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

    c.Print(fmt::format("{}_HcalRawHits_n.png", output_prefix).c_str());
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
    common_bench::plot::draw_label(ebeam, pbeam, detector);

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

    c.Print(fmt::format("{}_HcalRawHits_adc.png", output_prefix).c_str());
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
    common_bench::plot::draw_label(ebeam, pbeam, detector);

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

    c.Print(fmt::format("{}_HcalRawHits_tdc.png", output_prefix).c_str());
  }

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
