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
  eic::util::test vm_mass_resolution_test{
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
          .Define("mass_sim", util::get_im, {"decay_pair_sim"});

  // Define output histograms
  auto h_im_rec = d_im.Histo1D(
      {"h_im_rec", ";m_{ll'} (GeV);#", 100, -1.1, vm_mass + 5}, "mass_rec");
  auto h_im_sim = d_im.Histo1D(
      {"h_im_sim", ";m_{ll'} (GeV);#", 100, -1.1, vm_mass + 5}, "mass_sim");

  // Plot our histograms.
  // TODO: to start I'm explicitly plotting the histograms, but want to
  // factorize out the plotting code moving forward.
  {
    TCanvas c{"canvas", "canvas", 800, 800};
    gPad->SetLogx(false);
    gPad->SetLogy(false);
    auto& h0 = *h_im_sim;
    auto& h1 = *h_im_rec;
    // histogram style
    h0.SetLineColor(plot::kMpBlue);
    h0.SetLineWidth(2);
    h1.SetLineColor(plot::kMpOrange);
    h1.SetLineWidth(2);
    // axes
    h0.GetXaxis()->CenterTitle();
    h0.GetYaxis()->CenterTitle();
    // draw everything
    h0.DrawClone("hist");
    h1.DrawClone("hist same");
    // FIXME hardcoded beam configuration
    plot::draw_label(10, 100, detector, vm_name, "Invariant mass");
    TText* tptr;
    auto t = new TPaveText(.6, .8417, .9, .925, "NB NDC");
    t->SetFillColorAlpha(kWhite, 0);
    t->SetTextFont(43);
    t->SetTextSize(25);
    tptr = t->AddText("simulated");
    tptr->SetTextColor(plot::kMpBlue);
    tptr = t->AddText("reconstructed");
    tptr->SetTextColor(plot::kMpOrange);
    t->Draw();
    // Print canvas to output file
    c.Print(fmt::format("{}vm_mass.png", output_prefix).c_str());
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
