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

#include "fmt/color.h"
#include "fmt/core.h"
#include "nlohmann/json.hpp"

#include "eicd/ReconstructedParticleCollection.h"
#include "eicd/ReconstructedParticleData.h"

// Run VM invariant-mass-based benchmarks on an input reconstruction file for
// a desired vector meson (e.g. jpsi) and a desired decay particle (e.g. muon)
// Output figures are written to our output prefix (which includes the output
// file prefix), and labeled with our detector name.
// TODO: I think it would be better to pass small json configuration file to
//       the test, instead of this ever-expanding list of function arguments.
// FIXME: MC does not trace back into particle history. Need to fix that

//double RBW(double*x, double*par){
//    double mean = par[0];
//    double GAMMA = par[1];
//    double N = par[2];
//    double gamma = mean*TMath::Sqrt(mean*mean + GAMMA*GAMMA);
//    double k = 2.*mean*GAMMA*gamma/TMath::Pi()*TMath::Sqrt(2./(mean*mean + gamma));
//    double eval = N*k/((x[0]*x[0]-mean*mean)*(x[0]*x[0]-mean*mean) + mean*mean*GAMMA*GAMMA);
//    return(eval);
//}
//double fFlat(double*x, double*par){
//    return(par[0]);
//}
int vm_mass(const std::string& config_name)
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
  common_bench::Test mass_resolution_test{
      {{"name", fmt::format("{}_mass_resolution", test_tag, vm_name, decay_name)},
       {"title", fmt::format("{} Invariant Mass Resolution for {} -> {} with {}", vm_name, vm_name,
                             decay_name, detector)},
       {"description", "Invariant Mass Resolution calculated from raw "
                       "tracking data using a Gaussian fit."},
       {"quantity", "resolution"},
       {"target", ".2"}}};      //these 2 need to be consistent 
  double width_target = 0.2;    //going to find a way to use the same variable
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
  
  auto find_decay_pair = [vm_mass, decay_mass](const std::vector<ROOT::Math::PxPyPzMVector>& parts) {
    return common_bench::find_decay_pair(parts, vm_mass, decay_mass);
  };

  // common_bench::PrintGeant4(MCParticles);
  // Define analysis flow
  auto d_im = d.Define("p_rec", common_bench::momenta_RC, {"ReconstructedParticles"})       //using dummy rc
                  .Define("N", "p_rec.size()")
                  .Define("p_sim", common_bench::momenta_from_simulation, {"MCParticles"})
                  .Define("decay_pair_rec", find_decay_pair, {"p_rec"})
                  .Define("decay_pair_sim", find_decay_pair, {"p_sim"})
                  .Define("p_vm_rec", "decay_pair_rec.first + decay_pair_rec.second")
                  .Define("p_vm_sim", "decay_pair_sim.first + decay_pair_sim.second")
                  .Define("mass_rec", "p_vm_rec.M()")
                  .Define("mass_sim", "p_vm_sim.M()")
                  .Define("pt_rec", "p_vm_rec.pt()")
                  .Define("pt_sim", "p_vm_sim.pt()")
                  .Define("phi_rec", "p_vm_rec.phi()")
                  .Define("phi_sim", "p_vm_sim.phi()")
                  .Define("eta_rec", "p_vm_rec.eta()")
                  .Define("eta_sim", "p_vm_sim.eta()");

  // Define output histograms
  //auto h_im_rec = d_im.Histo1D({"h_im_rec", ";m_{ll'} (GeV/c^{2});#", (int)(vm_mass+0.5)*2*100, 0., 2.*(int)(vm_mass+0.5)}, "mass_rec"); //real rec 
  auto h_im_rec = d_im.Histo1D({"h_im_rec", ";m_{ll'} (GeV/c^{2});#", 30, 1.5, 4.5}, "mass_rec");//for dummy_rec
  auto h_im_sim = d_im.Histo1D({"h_im_sim", ";m_{ll'} (GeV/c^{2});#", 30, 1.5, 4.5}, "mass_sim");

  auto h_pt_rec = d_im.Histo1D({"h_pt_rec", ";p_{T} (GeV/c);#", 50, 0., 10.}, "pt_rec");
  auto h_pt_sim = d_im.Histo1D({"h_pt_sim", ";p_{T} (GeV/c);#", 50, 0., 10.}, "pt_sim");

  auto h_phi_rec = d_im.Histo1D({"h_phi_rec", ";#phi_{ll'};#", 45, -M_PI, M_PI}, "phi_rec");
  auto h_phi_sim = d_im.Histo1D({"h_phi_sim", ";#phi_{ll'};#", 45, -M_PI, M_PI}, "phi_sim");

  auto h_eta_rec = d_im.Histo1D({"h_eta_rec", ";#eta_{ll'};#", 50, -2., 2.}, "eta_rec");
  auto h_eta_sim = d_im.Histo1D({"h_eta_sim", ";#eta_{ll'};#", 50, -2., 2.}, "eta_sim");

  // Plot our histograms.
  // TODO: to start I'm explicitly plotting the histograms, but want to
  // factorize out the plotting code moving forward.
  //{
    TCanvas c{"canvas", "canvas", 1200, 1200};
    c.Divide(2, 2, 0.0001, 0.0001);
    // pad 1 mass
    c.cd(1);
    // gPad->SetLogx(false);
    // gPad->SetLogy(false);
    auto& h11 = *h_im_sim;
    auto& h12 = *h_im_rec;
    // histogram style
    h11.SetLineColor(common_bench::plot::kMpBlue);
    h11.SetLineWidth(2);
    h12.SetLineColor(common_bench::plot::kMpOrange);
    h12.SetLineWidth(1);
    // axes
    h11.GetXaxis()->CenterTitle();
    h11.GetYaxis()->CenterTitle();
    // draw everything
    h11.DrawClone("hist");
    h12.DrawClone("hist same");
    
    //Fit
    TF1* mfMass = new TF1("mfMass", "[2]*TMath::Gaus(x, [0], [1], kFALSE)", 1.5, 4.5);
    mfMass->SetParameters(3.096, 0.1, 100.);
    mfMass->SetParLimits(0, 3.0, 3.2);
    mfMass->SetParLimits(1, 0., 10.);
    mfMass->SetParLimits(2, 0., 1000.);
    mfMass->SetNpx(1000);
    mfMass->SetLineColor(2);
    mfMass->SetLineStyle(7);
    
    TFitResultPtr myFitPtr = h12.Fit(mfMass, "S 0", "", 1.5, 4.5);
    mfMass->Draw("same");
    
    // FIXME hardcoded beam configuration
    common_bench::plot::draw_label(10, 100, detector);                                                                                                               
    TText* tptr1;
    auto   t1 = new TPaveText(.6, .8417, .9, .925, "NB NDC");
    t1->SetFillColorAlpha(kWhite, 0);
    t1->SetTextFont(43);
    t1->SetTextSize(25);
    tptr1 = t1->AddText("simulated");
    tptr1->SetTextColor(common_bench::plot::kMpBlue);
    tptr1 = t1->AddText("reconstructed");
    tptr1->SetTextColor(common_bench::plot::kMpOrange);
    t1->Draw();

    // pad 2 pt
    c.cd(2);
    // gPad->SetLogx(false);
    // gPad->SetLogy(false);
    auto& h21 = *h_pt_sim;
    auto& h22 = *h_pt_rec;
    // histogram style
    h21.SetLineColor(common_bench::plot::kMpBlue);
    h21.SetLineWidth(2);
    h22.SetLineColor(common_bench::plot::kMpOrange);
    h22.SetLineWidth(1);
    // axes
    h21.GetXaxis()->CenterTitle();
    h21.GetYaxis()->CenterTitle();
    // draw everything
    h21.DrawClone("hist");
    h22.DrawClone("hist same");
    
    // FIXME hardcoded beam configuration
    common_bench::plot::draw_label(10, 100, detector);
    TText* tptr2;
    auto   t2 = new TPaveText(.6, .8417, .9, .925, "NB NDC");
    t2->SetFillColorAlpha(kWhite, 0);
    t2->SetTextFont(43);
    t2->SetTextSize(25);
    tptr2 = t2->AddText("simulated");
    tptr2->SetTextColor(common_bench::plot::kMpBlue);
    tptr2 = t2->AddText("reconstructed");
    tptr2->SetTextColor(common_bench::plot::kMpOrange);
    t2->Draw();

    // pad 3 phi
    c.cd(3);
    // gPad->SetLogx(false);
    // gPad->SetLogy(false);
    auto& h31 = *h_phi_sim;
    auto& h32 = *h_phi_rec;
    // histogram style
    h31.SetLineColor(common_bench::plot::kMpBlue);
    h31.SetLineWidth(2);
    h32.SetLineColor(common_bench::plot::kMpOrange);
    h32.SetLineWidth(1);
    // axes
    h31.GetXaxis()->CenterTitle();
    h31.GetYaxis()->CenterTitle();
    // draw everything
    h31.DrawClone("hist");
    h32.DrawClone("hist same");
    // FIXME hardcoded beam configuration
    common_bench::plot::draw_label(10, 100, detector);
    TText* tptr3;
    auto   t3 = new TPaveText(.6, .8417, .9, .925, "NB NDC");
    t3->SetFillColorAlpha(kWhite, 0);
    t3->SetTextFont(43);
    t3->SetTextSize(25);
    tptr3 = t3->AddText("simulated");
    tptr3->SetTextColor(common_bench::plot::kMpBlue);
    tptr3 = t3->AddText("reconstructed");
    tptr3->SetTextColor(common_bench::plot::kMpOrange);
    t3->Draw();

    // pad 4 rapidity
    c.cd(4);
    // gPad->SetLogx(false);
    // gPad->SetLogy(false);
    auto& h41 = *h_eta_sim;
    auto& h42 = *h_eta_rec;
    // histogram style
    h41.SetLineColor(common_bench::plot::kMpBlue);
    h41.SetLineWidth(2);
    h42.SetLineColor(common_bench::plot::kMpOrange);
    h42.SetLineWidth(1);
    // axes
    h41.GetXaxis()->CenterTitle();
    h41.GetYaxis()->CenterTitle();
    // draw everything
    h41.DrawClone("hist");
    h42.DrawClone("hist same");
    // FIXME hardcoded beam configuration
    common_bench::plot::draw_label(10, 100, detector);
    TText* tptr4;
    auto   t4 = new TPaveText(.6, .8417, .9, .925, "NB NDC");
    t4->SetFillColorAlpha(kWhite, 0);
    t4->SetTextFont(43);
    t4->SetTextSize(25);
    tptr4 = t4->AddText("simulated");
    tptr4->SetTextColor(common_bench::plot::kMpBlue);
    tptr4 = t4->AddText("reconstructed");
    tptr4->SetTextColor(common_bench::plot::kMpOrange);
    t4->Draw();

    c.Print(fmt::format("{}vm_mass_pt_phi_rapidity.png", output_prefix).c_str());
  //}

  // TODO we're not actually doing an IM fit yet, so for now just return an
  // error for the test result
  double width = mfMass->GetParameter(1);
  if(myFitPtr->Status()!=0){
    mass_resolution_test.error(-1);
  }else if(width > width_target){
    mass_resolution_test.fail(width);
  }else{
    mass_resolution_test.pass(width);
  }
  

  // write out our test data
  common_bench::write_test(mass_resolution_test, fmt::format("{}mass.json", output_prefix));

  // That's all!
  return 0;
}
