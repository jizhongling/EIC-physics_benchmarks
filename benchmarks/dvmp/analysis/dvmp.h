#ifndef DVMP_H
#define DVMP_H

#include <util.h>

#include <algorithm>
#include <cmath>
#include <exception>
#include <fmt/core.h>
#include <limits>
#include <string>
#include <vector>

#include <Math/Vector4D.h>

// Additional utility functions for DVMP benchmarks. Where useful, these can be
// promoted to the top-level util library
namespace util {

  //========================================================================================================
  // for structure functions

  struct inv_quant { // add more when needed
    double nu, Q2, x, t;
  };

  // for simu
  inline inv_quant calc_inv_quant_sim(const std::vector<ROOT::Math::PxPyPzMVector>& parts)
  {
    ROOT::Math::PxPyPzMVector q(parts[0] - parts[2]);
    ROOT::Math::PxPyPzMVector P(parts[3]);
    //ROOT::Math::PxPyPzMVector Delta(parts[6] - parts[3]);//exact jpsi
    ROOT::Math::PxPyPzMVector Delta(parts[0] - parts[2] - parts[7] - parts[8]);//jpsi->l l' gamma, ignore gamma

    double    nu         = q.Dot(P) / P.mass();
    double    Q2         = -q.Dot(q);
    double t = Delta.Dot(Delta);
    inv_quant quantities = {nu, Q2, Q2/2./P.mass()/nu, t};
    return quantities;
  }
  
 //for Dummy rc
  inline inv_quant calc_inv_quant_rec(const std::vector<ROOT::Math::PxPyPzMVector>& parts, const double pdg_mass, const double daughter_mass){
    int first = -1;
    int second = -1;
    double best_mass = -1;
    
    // go through all particle combinatorics, calculate the invariant mass
    // for each combination, and remember which combination is the closest
    // to the desired pdg_mass
    for (int i = 0; i < parts.size(); ++i) {
      if( fabs(parts[i].mass() - daughter_mass)/daughter_mass > 0.01) continue;
      for (int j = i + 1; j < parts.size(); ++j) {
        if( fabs(parts[j].mass() - daughter_mass)/daughter_mass > 0.01) continue;
        const double new_mass{(parts[i] + parts[j]).mass()};
        if (fabs(new_mass - pdg_mass) < fabs(best_mass - pdg_mass)) {
          first = i;
          second = j;
          best_mass = new_mass;
        }
      }
    }
    
    
    if (first < 0 || parts.size() < 3 ){      //fewer than 3 candidates 
      inv_quant quantities = {-99999., -99999., -99999., -99999.};
      return quantities;
    }
    
    //construct the beam kinematics
    ROOT::Math::PxPyPzMVector pair_4p(parts[first] + parts[second]);
    ROOT::Math::PxPyPzMVector e1, P;
    //double e1_Energy = sqrt(10.*10. + get_pdg_mass("electron")*get_pdg_mass("electron"));
    //double P_Energy = sqrt(100.*100. + get_pdg_mass("proton")*get_pdg_mass("proton"));
    double e1_Energy = sqrt((1.305e-8 - 10.)*(1.305e-8 - 10.) + (0.0005109+9.888e-8)*(0.0005109+9.888e-8));
    double P_Energy = sqrt((99.995598 + 1.313e-7)*(99.995598 + 1.313e-7) + (0.938272-1.23e-12)*(0.938272-1.23e-12));
    e1.SetPxPyPzE(0., 0., 1.305e-8 - 10., e1_Energy);
    P.SetPxPyPzE(0., 0., 99.995598 + 1.313e-7, P_Energy);
    int scatteredIdx = -1;
    
    //float dp = 10.;
    for(int i = 0 ; i < parts.size(); i++){
      if(i==first || i==second) continue;   //skip the paired leptons
      //if( fabs(parts[i].mass() - get_pdg_mass("electron"))/get_pdg_mass("electron") > 0.01) continue;
      if( fabs(parts[i].mass() - 0.0005109 - 9.888e-8)/(0.0005109 + 9.888e-8) > 0.01) continue;
      //ROOT::Math::PxPyPzMVector k_prime(parts[i]);  //scattered
      //float ptmp = sqrt(parts[i].px()*parts[i].px() + parts[i].py()*parts[i].py() + parts[i].pz()*parts[i].pz());
      //if( (k_prime.px()) * (pair_4p.px()) + (k_prime.py()) * (pair_4p.py()) + (k_prime.pz()) * (pair_4p.pz()) > 0. || ptmp >= 10.) continue; //angle between jpsi and scattered electron < pi/2, 3-momentum mag < 10. 
      //if(dp > 10.- ptmp){     //if there are more than one candidate of scattered electron, choose the one with highest 3-momentum mag
        scatteredIdx = i;
      //  dp = 10. - ptmp;
      //}
    }
    if(scatteredIdx ==-1){
      inv_quant quantities = {-99999., -99999., -99999., -99999.};
      return quantities;
    }
    ROOT::Math::PxPyPzMVector q(e1 - parts[scatteredIdx]);
    ROOT::Math::PxPyPzMVector Delta(q - pair_4p);

    double nu = q.Dot(P) / P.mass();
    double Q2 = - q.Dot(q);  
    double t = Delta.Dot(Delta);
    inv_quant quantities = {nu, Q2, Q2/2./P.mass()/nu, t};
    return quantities;
  }
  
  inline double get_nu(inv_quant quantities) { return quantities.nu / 1000.; }
  inline double get_Q2(inv_quant quantities) { return quantities.Q2; }
  inline double get_x(inv_quant quantities) { return quantities.x; }
  inline double get_t(inv_quant quantities) { return quantities.t; }

  // for tracking, add later

  //=========================================================================================================

} // namespace util

#endif
