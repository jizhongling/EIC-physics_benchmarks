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
//             .Define("n_B0PreshowerRawHits", "B0TrackerRawHits.size()")
//             .Define("n_B0TrackerRawHits",         "B0TrackerRawHits.size()")
             .Define("n_DRICHRawHits",             "DRICHRawHits.size()")
//             .Define("n_ERICHRawHits",             "ERICHRawHits.size()")
//             .Define("n_FakeDIRCRawHits",          "FakeDIRCRawHits.size()")
//             .Define("n_ffi_ZDC_ECALRawHits",      "ffi_ZDC_ECALRawHits.size()")
//            .Define("n_ffi_ZDC_HCALRawHits",      "ffi_ZDC_HCALRawHits.size()")
//             .Define("n_ForwardOffMTracker_station_1RawHits", "ForwardOffMTracker_station_1RawHits.size()")
//             .Define("n_ForwardOffMTracker_station_2RawHits", "ForwardOffMTracker_station_2RawHits.size()")
//             .Define("n_ForwardOffMTracker_station_3RawHits", "ForwardOffMTracker_station_3RawHits.size()")
 //            .Define("n_ForwardOffMTracker_station_4RawHits", "ForwardOffMTracker_station_4RawHits.size()")
 //            .Define("n_ForwardRomanPot_Station_1RawHits", "ForwardRomanPot_Status_1RawHits.size()")
 //            .Define("n_ForwardRomanPot_Station_2RawHits", "ForwardRomanPot_Status_2RawHits.size()")
 //            .Define("n_GEMEndcapNRawHits", "GEMEndcapNRawHits.size()")
 //            .Define("n_GEMEndcapPRawHits", "GEMEndcapPRawHits.size()")
 //            .Define("n_InnerTrackerBarrelRawHits", "InnerTrackerBarrelRawHits.size()")
//             .Define("n_InnerTrackerEndcapNRawHits", "InnerTrackerEndcapNRawHits.size()")
 //            .Define("n_InnerTrackerEndcapPRawHits", "InnerTrackerEndcapPRawHits.size()")
 //            .Define("n_MedialTrackerBarrelRawHits", "MedialTrackerBarrelRawHits.size()")
 //            .Define("n_MedialTrackerEndcapNRawHits", "MedialTrackerEndcapNRawHits.size()")
//             .Define("n_MedialTrackerEndcapPRawHits", "MedialTrackerEndcapPRawHits.size()")
 //            .Define("n_OuterTrackerBarrelRawHits", "OuterTrackerBarrelRawHits.size()")
 //            .Define("n_OuterTrackerEndcapNRawHits", "OuterTrackerEndcapNRawHits.size()")
 //            .Define("n_OuterTrackerEndcapPRawHits", "OuterTrackerEndcapPRawHits.size()")
             .Define("n_VertexBarrelRawHits", "VertexBarrelRawHits.size()")
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

  // other detector stats
  //auto stats_n_B0PreshowerRawHits = d0.Stats("n_B0PreshowerRawHits");
  //auto stats_n_B0TrackerRawHits = d0.Stats("n_B0TrackerRawHits");
  auto stats_n_DRICHRawHits = d0.Stats("n_DRICHRawHits");
 // auto stats_n_ERICHRawHits = d0.Stats("n_ERICHRawHits");
  //auto stats_n_FakeDIRCRawHits = d0.Stats("n_FakeDIRCRawHits");
  //auto stats_n_ffi_ZDC_ECALRawHits = d0.Stats("n_ffi_ZDC_ECALRawHits");
  //auto stats_n_ffi_ZDC_HCALRawHits = d0.Stats("n_ffi_ZDC_HCALRawHits");
  //auto stats_n_ForwardOffMTracker_station_1RawHits = d0.Stats("n_ForwardOffMTracker_station_1RawHits");
  //auto stats_n_ForwardOffMTracker_station_2RawHits = d0.Stats("n_ForwardOffMTracker_station_2RawHits");
  //auto stats_n_ForwardOffMTracker_station_3RawHits = d0.Stats("n_ForwardOffMTracker_station_3RawHits");
  //auto stats_n_ForwardOffMTracker_station_4RawHits = d0.Stats("n_ForwardOffMTracker_station_4RawHits");
  //auto stats_n_ForwardRomanPot_Station_1RawHits = d0.Stats("n_ForwardRomanPot_Station_1RawHits");
  //auto stats_n_ForwardRomanPot_Station_2RawHits = d0.Stats("n_ForwardRomanPot_Station_2RawHits");
  //auto stats_n_GEMEndcapNRawHits = d0.Stats("n_GEMEndcapNRawHits");
  //auto stats_n_GEMEndcapPRawHits = d0.Stats("n_GEMEndcapPRawHits");
  //auto stats_n_InnerTrackerBarrelRawHits = d0.Stats("n_InnerTrackerBarrelRawHits");
  //auto stats_n_InnerTrackerEndcapNRawHits = d0.Stats("n_InnerTrackerEndcapNRawHits");
  //auto stats_n_InnerTrackerEndcapPRawHits = d0.Stats("n_InnerTrackerEndcapPRawHits");
  //auto stats_n_MedialTrackerBarrelRawHits = d0.Stats("n_MedialTrackerBarrelRawHits");
  //auto stats_n_MedialTrackerEndcapNRawHits = d0.Stats("n_MedialTrackerEndcapNRawHits");
  //auto stats_n_MedialTrackerEndcapPRawHits = d0.Stats("n_MedialTrackerEndcapPRawHits");
  //auto stats_n_OuterTrackerBarrelRawHits = d0.Stats("n_OuterTrackerBarrelRawHits");
  //auto stats_n_OuterTrackerEndcapNRawHits = d0.Stats("n_OuterTrackerEndcapNRawHits");
  //auto stats_n_OuterTrackerEndcapPRawHits = d0.Stats("n_OuterTrackerEndcapPRawHits");
  auto stats_n_VertexBarrelRawHits = d0.Stats("n_VertexBarrelRawHits");

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

  // other detector stats
  //fmt::print("B0PreshowerRawHits:");
  //stats_n_B0PreshowerRawHits->Print();
  //fmt::print("B0TrackerRawHits:");
  //stats_n_B0TrackerRawHits->Print();
  fmt::print("n_DRICHRawHits:");
  stats_n_DRICHRawHits->Print();
  //fmt::print("n_ERICHRawHits:");
 // stats_n_ERICHRawHits->Print();
  //fmt::print("n_FakeDIRCRawHits:");
  //stats_n_FakeDIRCRawHits->Print();
  //fmt::print("n_ffi_ZDC_ECALRawHits:");
  //stats_n_ffi_ZDC_ECALRawHits->Print();
  //fmt::print("n_ffi_ZDC_HCALRawHits:");
  //stats_n_ffi_ZDC_HCALRawHits->Print();
  //fmt::print("n_ForwardOffMTracker_station_1RawHits:");
  //stats_n_ForwardOffMTracker_station_1RawHits->Print();
  //fmt::print("n_ForwardOffMTracker_station_2RawHits:");
  //stats_n_ForwardOffMTracker_station_2RawHits->Print();
  //fmt::print("n_ForwardOffMTracker_station_3RawHits:");
  //stats_n_ForwardOffMTracker_station_3RawHits->Print();
  //fmt::print("n_ForwardOffMTracker_station_4RawHits:");
  //stats_n_ForwardOffMTracker_station_4RawHits->Print();
  //fmt::print("n_ForwardOffMTracker_station_1RawHits:");
  //stats_n_ForwardRomanPot_Station_1RawHits->Print();
  //fmt::print("n_ForwardOffMTracker_station_2RawHits:");
  //stats_n_ForwardRomanPot_Station_2RawHits->Print();
  //fmt::print("n_GEMEndcapNRawHits:");
  //stats_n_GEMEndcapNRawHits->Print();
  //fmt::print("n_GEMEndcapPRawHits:");
  //stats_n_GEMEndcapPRawHits->Print();
  //fmt::print("n_InnerTrackerBarrelRawHits:");
  //stats_n_InnerTrackerBarrelRawHits->Print();
  //fmt::print("n_InnerTrackerEndcapNRawHits:");
  //stats_n_InnerTrackerEndcapNRawHits->Print();
  //fmt::print("n_InnerTrackerEndcapPRawHits:");
  //stats_n_InnerTrackerEndcapPRawHits->Print();
  //fmt::print("n_MedialTrackerBarrelRawHits:");
  //stats_n_MedialTrackerBarrelRawHits->Print();
  //fmt::print("n_MedialTrackerEndcapNRawHits:");
  //stats_n_MedialTrackerEndcapNRawHits->Print(); 
  //fmt::print("n_MedialTrackerEndcapPRawHits:");
  //stats_n_MedialTrackerEndcapPRawHits->Print();
  //fmt::print("n_OuterTrackerBarrelRawHits:");   
  //stats_n_OuterTrackerBarrelRawHits->Print();
  //fmt::print("n_OuterTrackerEndcapNRawHits:");
  //stats_n_OuterTrackerEndcapNRawHits->Print(); 
  //fmt::print("n_OuterTrackerEndcapPRawHits:");
  //->Print();
  fmt::print("n_VertexBarrelRawHits:");
  stats_n_VertexBarrelRawHits->Print(); 
  
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
