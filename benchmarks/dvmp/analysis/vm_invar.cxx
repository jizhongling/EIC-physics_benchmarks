#include "dvmp.h"
#include "plot.h"

#include <benchmark.h>
#include <mt.h>
#include <util.h>

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
// FIXME: MC does not trace back into particle history. Need to fix that
int vm_invar(const std::string& config_name)
{
  // read our configuration
  std::ifstream  config_file{config_name};
  nlohmann::json config;
  config_file >> config;

  const std::string rec_file      = config["rec_file"];
  const std::string vm_name       = config["vm_name"];
  const std::string decay_name    = config["decay"];
  const std::string detector      = config["detector"];
  std::string       output_prefix = config["output_prefix"];
  const std::string test_tag      = config["test_tag"];

  fmt::print(fmt::emphasis::bold | fg(fmt::color::forest_green),
             "Running VM invariant mass analysis...\n");
  fmt::print(" - Vector meson: {}\n", vm_name);
  fmt::print(" - Decay particle: {}\n", decay_name);
  fmt::print(" - Detector package: {}\n", detector);
  fmt::print(" - input file: {}\n", rec_file);
  fmt::print(" - output prefix: {}\n", output_prefix);

  // create our test definition
  // test_tag
  eic::util::Test Q2_resolution_test{
      {{"name", fmt::format("{}_Q2_resolution", test_tag)},
       {"title",
        fmt::format("Q^2 Resolution for {} -> {} events with {}", vm_name, decay_name, detector)},
       {"description", "Invariant Mass Resolution calculated from raw "
                       "tracking data using a Gaussian fit."},
       {"quantity", "resolution"},
       {"target", ".1"}}};

  // Run this in multi-threaded mode if desired
  ROOT::EnableImplicitMT(kNumThreads);

  // The particles we are looking for. E.g. J/psi decaying into e+e-
  const double vm_mass    = util::get_pdg_mass(vm_name);
  const double decay_mass = util::get_pdg_mass(decay_name);

  // Ensure our output prefix always ends on a dot, a slash or a dash
  if (output_prefix.back() != '.' && output_prefix.back() != '/' && output_prefix.back() != '-') {
    output_prefix += "-";
  }

  // Open our input file file as a dataframe
  ROOT::RDataFrame d{"events", rec_file};

  // utility lambda functions to bind the vector meson and decay particle
  // types
  auto momenta_from_tracking = [decay_mass](const std::vector<eic::TrackParametersData>& tracks) {
    return util::momenta_from_tracking(tracks, decay_mass);
  };

  //====================================================================

  // Define analysis flow
  auto d_im = d.Define("p_rec", momenta_from_tracking, {"outputTrackParameters"})
                  .Define("N", "p_rec.size()")
                  .Define("p_sim", util::momenta_from_simulation, {"mcparticles2"})
                  //================================================================
                  .Define("invariant_quantities", util::calc_inv_quant_simu, {"p_sim"})
                  .Define("nu_sim", util::get_nu_simu, {"invariant_quantities"})
                  .Define("Q2_sim", util::get_Q2_simu, {"invariant_quantities"})
                  .Define("x_sim", util::get_x_simu, {"invariant_quantities"});
  //================================================================

  // Define output histograms

  auto h_nu_sim = d_im.Histo1D({"h_nu_sim", ";#nu/1000;#", 100, 0., 2.}, "nu_sim");
  auto h_Q2_sim = d_im.Histo1D({"h_Q2_sim", ";Q^{2};#", 100, 0., 15.}, "Q2_sim");
  auto h_x_sim  = d_im.Histo1D({"h_x_sim", ";x;#", 100, 0., 0.1}, "x_sim");

  // Plot our histograms.
  // TODO: to start I'm explicitly plotting the histograms, but want to
  // factorize out the plotting code moving forward.
  {

    // Print canvas to output file

    TCanvas c{"canvas2", "canvas2", 1800, 600};
    c.Divide(3, 1, 0.0001, 0.0001);
    // pad 1 nu
    c.cd(1);
    // gPad->SetLogx(false);
    // gPad->SetLogy(false);
    auto& hnu = *h_nu_sim;
    // histogram style
    hnu.SetLineColor(plot::kMpBlue);
    hnu.SetLineWidth(2);
    // axes
    hnu.GetXaxis()->CenterTitle();
    // hnu.GetXaxis()->SetTitle("#times1000");
    // draw everything
    hnu.DrawClone("hist");
    // FIXME hardcoded beam configuration
    plot::draw_label(10, 100, detector);
    TText* tptr21;
    auto   t21 = new TPaveText(.6, .8417, .9, .925, "NB NDC");
    t21->SetFillColorAlpha(kWhite, 0);
    t21->SetTextFont(43);
    t21->SetTextSize(25);
    tptr21 = t21->AddText("simulated");
    tptr21->SetTextColor(plot::kMpBlue);
    // tptr1 = t1->AddText("reconstructed");
    // tptr1->SetTextColor(plot::kMpOrange);
    t21->Draw();

    // pad 2 Q2
    c.cd(2);
    // gPad->SetLogx(false);
    // gPad->SetLogy(false);
    auto& hQ2 = *h_Q2_sim;
    // histogram style
    hQ2.SetLineColor(plot::kMpBlue);
    hQ2.SetLineWidth(2);
    // axes
    hQ2.GetXaxis()->CenterTitle();
    // draw everything
    hQ2.DrawClone("hist");
    // FIXME hardcoded beam configuration
    plot::draw_label(10, 100, detector);
    TText* tptr22;
    auto   t22 = new TPaveText(.6, .8417, .9, .925, "NB NDC");
    t22->SetFillColorAlpha(kWhite, 0);
    t22->SetTextFont(43);
    t22->SetTextSize(25);
    tptr22 = t22->AddText("simulated");
    tptr22->SetTextColor(plot::kMpBlue);
    // tptr1 = t1->AddText("reconstructed");
    // tptr1->SetTextColor(plot::kMpOrange);
    t22->Draw();

    // pad 1 nu
    c.cd(3);
    // gPad->SetLogx(false);
    // gPad->SetLogy(false);
    auto& hx = *h_x_sim;
    // histogram style
    hx.SetLineColor(plot::kMpBlue);
    hx.SetLineWidth(2);
    // axes
    hx.GetXaxis()->CenterTitle();
    // draw everything
    hx.DrawClone("hist");
    // FIXME hardcoded beam configuration
    plot::draw_label(10, 100, detector);
    TText* tptr23;
    auto   t23 = new TPaveText(.6, .8417, .9, .925, "NB NDC");
    t23->SetFillColorAlpha(kWhite, 0);
    t23->SetTextFont(43);
    t23->SetTextSize(25);
    tptr23 = t23->AddText("simulated");
    tptr23->SetTextColor(plot::kMpBlue);
    // tptr1 = t1->AddText("reconstructed");
    // tptr1->SetTextColor(plot::kMpOrange);
    t23->Draw();

    c.Print(fmt::format("{}InvariantQuantities.png", output_prefix).c_str());
  }

  // TODO we're not actually getting the resolutions yet
  // error for the test result
  Q2_resolution_test.error(-1);

  // write out our test data
  eic::util::write_test(Q2_resolution_test, fmt::format("{}invar.json", output_prefix));

  // That's all!
  return 0;
}
