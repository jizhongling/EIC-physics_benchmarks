#include "benchmark.hh"
#include "mt.h"
#include "plot.h"
#include "util.h"

#include <ROOT/RDataFrame.hxx>
#include <cmath>
#include <fmt/color.h>
#include <fmt/core.h>
#include <fstream>
#include <iostream>
#include <nlohmann/json.hpp>
#include <string>
#include <vector>

// Run VM invariant-mass-based benchmarks on an input reconstruction file for
// a desired vector meson (e.g. jpsi) and a desired decay particle (e.g. muon)
// Output figures are written to our output prefix (which includes the output
// file prefix), and labeled with our detector name.
// TODO: I think it would be better to pass small json configuration file to
//       the test, instead of this ever-expanding list of function arguments.
int vm_mass(const std::string& config_name) {
  // read our configuration
  std::ifstream config_file{config_name};
  nlohmann::json config;
  config_file >> config;

  const std::string rec_file = config["rec_file"];
  const std::string vm_name = config["vm_name"];
  const std::string decay_name = config["decay"];
  const std::string detector = config["detector"];
  std::string output_prefix = config["output_prefix"];
  const std::string test_tag = config["test_tag"];

  fmt::print(fmt::emphasis::bold | fg(fmt::color::forest_green),
             "Running VM invariant mass analysis...\n");
  fmt::print(" - Vector meson: {}\n", vm_name);
  fmt::print(" - Decay particle: {}\n", decay_name);
  fmt::print(" - Detector package: {}\n", detector);
  fmt::print(" - output prefix: {}\n", output_prefix);

  // create our test definition
  // test_tag
  eic::util::Test vm_mass_resolution_test{
      {{"name",
        fmt::format("{}_{}_{}_mass_resolution", test_tag, vm_name, decay_name)},
       {"title",
        fmt::format("{} -> {} Invariant Mass Resolution", vm_name, decay_name)},
       {"description", "Invariant Mass Resolution calculated from raw "
                       "tracking data using a Gaussian fit."},
       {"quantity", "resolution"},
       {"target", ".1"}}};

  // Run this in multi-threaded mode if desired
  ROOT::EnableImplicitMT(kNumThreads);

  // The particles we are looking for. E.g. J/psi decaying into e+e-
  const double vm_mass = util::get_pdg_mass(vm_name);
  const double decay_mass = util::get_pdg_mass(decay_name);

  // Ensure our output prefix always ends on a dot, a slash or a dash
  if (output_prefix.back() != '.' && output_prefix.back() != '/' &&
      output_prefix.back() != '-') {
    output_prefix += "-";
  }

  // Open our input file file as a dataframe
  ROOT::RDataFrame d{"events", rec_file};

  // utility lambda functions to bind the vector meson and decay particle
  // types
  auto momenta_from_tracking =
      [decay_mass](const std::vector<eic::TrackParametersData>& tracks) {
        return util::momenta_from_tracking(tracks, decay_mass);
      };
  auto find_decay_pair =
      [vm_mass](const std::vector<ROOT::Math::PxPyPzMVector>& parts) {
        return util::find_decay_pair(parts, vm_mass);
      };

  // Define analysis flow
  auto d_im =
      d.Define("p_rec", momenta_from_tracking, {"outputTrackParameters"})
          .Define("N", "p_rec.size()")
          .Define("p_sim", util::momenta_from_simulation, {"mcparticles2"})
          .Define("decay_pair_rec", find_decay_pair, {"p_rec"})
          .Define("decay_pair_sim", find_decay_pair, {"p_sim"})
          .Define("mass_rec", util::get_im, {"decay_pair_rec"})
          .Define("mass_sim", util::get_im, {"decay_pair_sim"})
          .Define("pt_rec", util::get_pt, {"decay_pair_rec"})
          .Define("pt_sim", util::get_pt, {"decay_pair_sim"})
          .Define("phi_rec" , util::get_phi, {"decay_pair_rec"})
          .Define("phi_sim" , util::get_phi, {"decay_pair_sim"})
          .Define("rapidity_rec" , util::get_y, {"decay_pair_rec"})
          .Define("rapidity_sim" , util::get_y, {"decay_pair_sim"});

  // Define output histograms
  auto h_im_rec = d_im.Histo1D(
      {"h_im_rec", ";m_{ll'} (GeV/c^{2});#", 100, -1.1, vm_mass + 5}, "mass_rec");
  auto h_im_sim = d_im.Histo1D(
      {"h_im_sim", ";m_{ll'} (GeV/c^{2});#", 100, -1.1, vm_mass + 5}, "mass_sim");
      
  auto h_pt_rec = d_im.Histo1D(
      {"h_pt_rec", ";p_{T} (GeV/c);#", 400, 0., 40.}, "pt_rec");
  auto h_pt_sim = d_im.Histo1D(
      {"h_pt_sim", ";p_{T} (GeV/c);#", 400, 0., 40.}, "pt_sim"); 
      
  auto h_phi_rec = d_im.Histo1D(
      {"h_phi_rec", ";#phi_{ll'};#", 90, -M_PI, M_PI}, "phi_rec");
  auto h_phi_sim = d_im.Histo1D(
      {"h_phi_sim", ";#phi_{ll'};#", 90, -M_PI, M_PI}, "phi_sim");
      
  auto h_y_rec = d_im.Histo1D(
      {"h_y_rec", ";y_{ll'};#", 1000, -5., 5.}, "rapidity_rec");
  auto h_y_sim = d_im.Histo1D(
      {"h_y_sim", ";y_{ll'};#", 1000, -5., 5.}, "rapidity_sim");


  // Plot our histograms.
  // TODO: to start I'm explicitly plotting the histograms, but want to
  // factorize out the plotting code moving forward.
  {
    TCanvas c{"canvas", "canvas", 1200, 1200};
    c.Divide(2, 2, 0.0001, 0.0001);
    //pad 1 mass
    c.cd(1);
    //gPad->SetLogx(false);
    //gPad->SetLogy(false);
    auto& h11 = *h_im_sim;
    auto& h12 = *h_im_rec;
    // histogram style
    h11.SetLineColor(plot::kMpBlue);
    h11.SetLineWidth(2);
    h12.SetLineColor(plot::kMpOrange);
    h12.SetLineWidth(2);
    // axes
    h11.GetXaxis()->CenterTitle();
    h11.GetYaxis()->CenterTitle();
    // draw everything
    h11.DrawClone("hist");
    h12.DrawClone("hist same");
    // FIXME hardcoded beam configuration
    plot::draw_label(10, 100, detector, vm_name, "Invariant mass");
    TText* tptr1;
    auto t1 = new TPaveText(.6, .8417, .9, .925, "NB NDC");
    t1->SetFillColorAlpha(kWhite, 0);
    t1->SetTextFont(43);
    t1->SetTextSize(25);
    tptr1 = t1->AddText("simulated");
    tptr1->SetTextColor(plot::kMpBlue);
    tptr1 = t1->AddText("reconstructed");
    tptr1->SetTextColor(plot::kMpOrange);
    t1->Draw();
    
    //pad 2 pt
    c.cd(2);
    //gPad->SetLogx(false);
    //gPad->SetLogy(false);
    auto& h21 = *h_pt_sim;
    auto& h22 = *h_pt_rec;
    // histogram style
    h21.SetLineColor(plot::kMpBlue);
    h21.SetLineWidth(2);
    h22.SetLineColor(plot::kMpOrange);
    h22.SetLineWidth(2);
    // axes
    h21.GetXaxis()->CenterTitle();
    h21.GetYaxis()->CenterTitle();
    // draw everything
    h21.DrawClone("hist");
    h22.DrawClone("hist same");
    // FIXME hardcoded beam configuration
    plot::draw_label(10, 100, detector, vm_name, "Transverse Momentum");
    TText* tptr2;
    auto t2 = new TPaveText(.6, .8417, .9, .925, "NB NDC");
    t2->SetFillColorAlpha(kWhite, 0);
    t2->SetTextFont(43);
    t2->SetTextSize(25);
    tptr2 = t2->AddText("simulated");
    tptr2->SetTextColor(plot::kMpBlue);
    tptr2 = t2->AddText("reconstructed");
    tptr2->SetTextColor(plot::kMpOrange);
    t2->Draw();
    
    //pad 3 phi
    c.cd(3);
    //gPad->SetLogx(false);
    //gPad->SetLogy(false);
    auto& h31 = *h_phi_sim;
    auto& h32 = *h_phi_rec;
    // histogram style
    h31.SetLineColor(plot::kMpBlue);
    h31.SetLineWidth(2);
    h32.SetLineColor(plot::kMpOrange);
    h32.SetLineWidth(2);
    // axes
    h31.GetXaxis()->CenterTitle();
    h31.GetYaxis()->CenterTitle();
    // draw everything
    h31.DrawClone("hist");
    h32.DrawClone("hist same");
    // FIXME hardcoded beam configuration
    plot::draw_label(10, 100, detector, vm_name, "#phi");
    TText* tptr3;
    auto t3 = new TPaveText(.6, .8417, .9, .925, "NB NDC");
    t3->SetFillColorAlpha(kWhite, 0);
    t3->SetTextFont(43);
    t3->SetTextSize(25);
    tptr3 = t3->AddText("simulated");
    tptr3->SetTextColor(plot::kMpBlue);
    tptr3 = t3->AddText("reconstructed");
    tptr3->SetTextColor(plot::kMpOrange);
    t3->Draw();
    
    //pad 4 rapidity
    c.cd(4);
    //gPad->SetLogx(false);
    //gPad->SetLogy(false);
    auto& h41 = *h_y_sim;
    auto& h42 = *h_y_rec;
    // histogram style
    h41.SetLineColor(plot::kMpBlue);
    h41.SetLineWidth(2);
    h42.SetLineColor(plot::kMpOrange);
    h42.SetLineWidth(2);
    // axes
    h41.GetXaxis()->CenterTitle();
    h41.GetYaxis()->CenterTitle();
    // draw everything
    h41.DrawClone("hist");
    h42.DrawClone("hist same");
    // FIXME hardcoded beam configuration
    plot::draw_label(10, 100, detector, vm_name, "Rapidity");
    TText* tptr4;
    auto t4 = new TPaveText(.6, .8417, .9, .925, "NB NDC");
    t4->SetFillColorAlpha(kWhite, 0);
    t4->SetTextFont(43);
    t4->SetTextSize(25);
    tptr4 = t4->AddText("simulated");
    tptr4->SetTextColor(plot::kMpBlue);
    tptr4 = t4->AddText("reconstructed");
    tptr4->SetTextColor(plot::kMpOrange);
    t4->Draw();
    
    // Print canvas to output file
    c.Print(fmt::format("{}vm_mass_pt_phi_rapidity.png", output_prefix).c_str());
  }

  // TODO we're not actually doing an IM fit yet, so for now just return an
  // error for the test result
  vm_mass_resolution_test.error(-1);

  // write out our test data
  eic::util::write_test(vm_mass_resolution_test,
                           fmt::format("{}vm_mass.json", output_prefix));

  // That's all!
  return 0;
}
