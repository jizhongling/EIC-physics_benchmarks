#include "dvmp.h"

#include "common_bench/plot.h"
#include "common_bench/benchmark.h"
#include "common_bench/mt.h"
#include "common_bench/util.h"

#include "ROOT/RDataFrame.hxx"

#include <cmath>
#include <fstream>
#include <iostream>
#include <string>
#include <vector>

#include "nlohmann/json.hpp"
#include "fmt/color.h"
#include "fmt/core.h"

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
  common_bench::Test Q2_resolution_test{
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
  const double vm_mass    = common_bench::get_pdg_mass(vm_name);
  const double decay_mass = common_bench::get_pdg_mass(decay_name);

  // Ensure our output prefix always ends on a dot, a slash or a dash
  if (output_prefix.back() != '.' && output_prefix.back() != '/' && output_prefix.back() != '-') {
    output_prefix += "-";
  }

  // Open our input file file as a dataframe
  ROOT::RDataFrame d{"events", rec_file};

  // utility lambda functions to bind the vector meson and decay particle
  // types
  
  auto momenta_sort_sim = [vm_name, decay_name](const std::vector<dd4pod::Geant4ParticleData>& parts){
    return util::momenta_sort_sim(parts, vm_name, decay_name);
  };
  auto momenta_sort_rec = [vm_name, decay_name](const std::vector<eic::ReconstructedParticleData>& parts){
    return util::momenta_sort_rec(parts, vm_name, decay_name);
  };
  //====================================================================

  // Define analysis flow
  auto d_im = d.Define("p_rec_sorted", momenta_sort_rec, {"ReconstructedParticles"})
                  .Define("p_sim_sorted", momenta_sort_sim, {"mcparticles2"})
                  .Define("N", "p_rec_sorted.size()")
                  .Define("invariant_quantities_rec", util::calc_inv_quant, {"p_rec_sorted"})
                  .Define("invariant_quantities_sim", util::calc_inv_quant, {"p_sim_sorted"})
                  .Define("y_rec", util::get_y, {"invariant_quantities_rec"})
                  .Define("Q2_rec", util::get_Q2, {"invariant_quantities_rec"})
                  .Define("x_rec", util::get_x, {"invariant_quantities_rec"})
                  .Define("t_rec", util::get_t, {"invariant_quantities_rec"})
                  .Define("y_sim", util::get_y, {"invariant_quantities_sim"})
                  .Define("Q2_sim", util::get_Q2, {"invariant_quantities_sim"})
                  .Define("x_sim", util::get_x, {"invariant_quantities_sim"})
                  .Define("t_sim", util::get_t, {"invariant_quantities_sim"});
                  
  //================================================================

  // Define output histograms

  //auto h_nu_sim = d_im.Histo1D({"h_nu_sim", ";#nu/1000;#", 100, 0., 2.}, "nu_sim");
  auto h_Q2_sim = d_im.Histo1D({"h_Q2_sim", ";Q^{2};#", 50, 0., 15.}, "Q2_sim");
  auto h_x_sim  = d_im.Histo1D({"h_x_sim", ";x;#", 50, 0., 0.1}, "x_sim");
  auto h_y_sim  = d_im.Histo1D({"h_y_sim", ";y;#", 50, 0., 1.}, "y_sim");
  auto h_t_sim  = d_im.Histo1D({"h_t_sim", ";t;#", 50, -1., 0.}, "t_sim");
  
  
  //auto h_nu_rec = d_im.Histo1D({"h_nu_rec", ";#nu/1000;#", 100, 0., 2.}, "nu_rec");
  auto h_Q2_rec = d_im.Histo1D({"h_Q2_rec", ";Q^{2};#", 50, 0., 15.}, "Q2_rec");
  auto h_x_rec  = d_im.Histo1D({"h_x_rec", ";x;#", 50, 0., 0.1}, "x_rec");
  auto h_y_rec  = d_im.Histo1D({"h_y_rec", ";y;#", 50, 0., 1.}, "y_rec");
  auto h_t_rec  = d_im.Histo1D({"h_t_rec", ";t;#", 50, -1., 0.}, "t_rec");
  
  // Plot our histograms.
  // TODO: to start I'm explicitly plotting the histograms, but want to
  // factorize out the plotting code moving forward.
  {

    // Print canvas to output file

    TCanvas c{"canvas2", "canvas2", 1200, 900};
    c.Divide(2, 2, 0.0001, 0.0001);
    // pad 1 nu
    c.cd(1);
    auto& hy_rec = *h_y_rec;
    auto& hy_sim = *h_y_sim;
    // histogram style
    hy_rec.SetLineColor(common_bench::plot::kMpOrange);
    hy_rec.SetLineWidth(1);
    hy_sim.SetLineColor(common_bench::plot::kMpBlue);
    hy_sim.SetLineWidth(2);
    // axes
    hy_sim.GetXaxis()->CenterTitle();
    // draw everything
    hy_sim.DrawClone("hist");
    hy_rec.DrawClone("hist same");
    // FIXME hardcoded beam configuration
    common_bench::plot::draw_label(10, 100, detector);
    TText* tptr1;
    auto   t1 = new TPaveText(.6, .8417, .9, .925, "NB NDC");
    t1->SetFillColorAlpha(kWhite, 0);
    t1->SetTextFont(43);
    t1->SetTextSize(25);
    tptr1 = t1->AddText("simulated");
    tptr1->SetTextColor(common_bench::plot::kMpBlue);
    tptr1 = t1->AddText("rec(PlaceHolder)");
    tptr1->SetTextColor(common_bench::plot::kMpOrange);
    t1->Draw();

    // pad 2 Q2
    c.cd(2);
    auto& hQ2_rec = *h_Q2_rec;
    auto& hQ2_sim = *h_Q2_sim;
    // histogram style
    hQ2_rec.SetLineColor(common_bench::plot::kMpOrange);
    hQ2_rec.SetLineWidth(1);
    hQ2_sim.SetLineColor(common_bench::plot::kMpBlue);
    hQ2_sim.SetLineWidth(2);
    // axes
    hQ2_sim.GetXaxis()->CenterTitle();
    // draw everything
    hQ2_sim.DrawClone("hist");
    hQ2_rec.DrawClone("hist same");
    // FIXME hardcoded beam configuration
    common_bench::plot::draw_label(10, 100, detector);
    TText* tptr2;
    auto   t2 = new TPaveText(.6, .8417, .9, .925, "NB NDC");
    t2->SetFillColorAlpha(kWhite, 0);
    t2->SetTextFont(43);
    t2->SetTextSize(25);
    tptr2 = t2->AddText("simulated");
    tptr2->SetTextColor(common_bench::plot::kMpBlue);
    tptr2 = t2->AddText("rec(PlaceHolder)");
    tptr2->SetTextColor(common_bench::plot::kMpOrange);
    t2->Draw();
    
    // pad 3 x
    c.cd(3);
    auto& hx_rec = *h_x_rec;
    auto& hx_sim = *h_x_sim;
    // histogram style
    hx_rec.SetLineColor(common_bench::plot::kMpOrange);
    hx_rec.SetLineWidth(1);
    hx_sim.SetLineColor(common_bench::plot::kMpBlue);
    hx_sim.SetLineWidth(2);
    // axes
    hx_sim.GetXaxis()->CenterTitle();
    // draw everything
    hx_sim.DrawClone("hist");
    hx_rec.DrawClone("hist same");
    // FIXME hardcoded beam configuration
    common_bench::plot::draw_label(10, 100, detector);
    TText* tptr3;
    auto   t3 = new TPaveText(.6, .8417, .9, .925, "NB NDC");
    t3->SetFillColorAlpha(kWhite, 0);
    t3->SetTextFont(43);
    t3->SetTextSize(25);
    tptr3 = t3->AddText("simulated");
    tptr3->SetTextColor(common_bench::plot::kMpBlue);
    tptr3 = t3->AddText("rec(PlaceHolder)");
    tptr3->SetTextColor(common_bench::plot::kMpOrange);
    t3->Draw();
    
    // pad 4 t
    c.cd(4);
    auto& ht_rec = *h_t_rec;
    auto& ht_sim = *h_t_sim;
    // histogram style
    ht_rec.SetLineColor(common_bench::plot::kMpOrange);
    ht_rec.SetLineWidth(1);
    ht_sim.SetLineColor(common_bench::plot::kMpBlue);
    ht_sim.SetLineWidth(2);
    // axes
    ht_sim.GetXaxis()->CenterTitle();
    // draw everything
    ht_sim.DrawClone("hist");
    ht_rec.DrawClone("hist same");
    // FIXME hardcoded beam configuration
    common_bench::plot::draw_label(10, 100, detector);
    TText* tptr4;
    auto   t4 = new TPaveText(.6, .8417, .9, .925, "NB NDC");
    t4->SetFillColorAlpha(kWhite, 0);
    t4->SetTextFont(43);
    t4->SetTextSize(25);
    tptr4 = t4->AddText("simulated");
    tptr4->SetTextColor(common_bench::plot::kMpBlue);
    tptr4 = t4->AddText("rec(PlaceHolder)");
    tptr4->SetTextColor(common_bench::plot::kMpOrange);
    t4->Draw();
    
    c.Print(fmt::format("{}InvariantQuantities.png", output_prefix).c_str());
    
    
  }

  // TODO we're not actually getting the resolutions yet
  // error for the test result
  Q2_resolution_test.error(-1);

  // write out our test data
  common_bench::write_test(Q2_resolution_test, fmt::format("{}invar.json", output_prefix));

  // That's all!
  return 0;
}
