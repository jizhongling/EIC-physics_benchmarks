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
    double nu, Q2, x, y, t;
  };
  //import Geant4 and set the wanted particles in the intended order
  //0:e0  1:p0    2:e1    3:p1    4:recoil system (without p1)    5:l1 from 4 6:l2 from 4
  inline auto momenta_sort_sim(const std::vector<dd4pod::Geant4ParticleData>& parts, std::string_view mother, std::string_view daughter){//mother and daughter are not used yet; will be useful when generater is different and/or when the mcparticles doesn't follow the same order in all events
    std::vector<ROOT::Math::PxPyPzMVector> momenta{7};
    int order_map[7] = {0, 3, 2, 6, 5, 7, 8};             
    for(int i = 0 ; i < 7 ; i++){
      double px = parts[order_map[i]].psx;
      double py = parts[order_map[i]].psy;
      double pz = parts[order_map[i]].psz;
      double mass = parts[order_map[i]].mass;
      double e = sqrt(px*px + py*py + pz*pz + mass*mass);
      momenta[i].SetPxPyPzE(px, py, pz, e);
    }
    //for(int i = 0 ; i < 7 ; i++){
    //    cout<<Form("sim, idx = %d, P(px, py, pz, mass) = (%f, %f, %f, %f)", i, momenta[i].px(), momenta[i].py(), momenta[i].pz(), momenta[i].mass())<<endl;
    //}
    //cout<<"========================================="<<endl;
    return momenta;
  }
  
  //import Reconstructed particles and set the wanted particles in the intended order========================
  inline auto momenta_sort_rec(const std::vector<eic::ReconstructedParticleData>& parts, std::string_view mother, std::string_view daughter){
    std::vector<ROOT::Math::PxPyPzMVector> momenta{7};
    //0:e0  1:p0    2:e1    3:p1    4:recoil system (without p1)    5:l1 from recoil decay  6:l2 from recoil decay
    for(int i = 0 ; i < 7 ; i++) momenta[i].SetPxPyPzE(0., 0., 0., 0.);   //initialize as all 0
    
    //manually set incoming electron and proton;
    double e0_mass = get_pdg_mass("electron");
    double e0_pz = 1.305e-8 - 10.;
    momenta[0].SetPxPyPzE(0., 0., e0_pz, sqrt(e0_mass*e0_mass + e0_pz*e0_pz));
    double p0_mass = get_pdg_mass("proton");
    double p0_pz = 99.995598 + 1.313e-7 + 8.783e-11;
    momenta[1].SetPxPyPzE(0., 0., p0_pz, sqrt(p0_mass*p0_mass + p0_pz*p0_pz));
    
    //FIXME search for recoil proton, add feature to deal with multiple protons in one event
    for(int i = 0 ; i < parts.size() ; i++){
      if(parts[i].pid!=2212) continue;
      //px, py, pz, e, mass are not consistent for smeared dummy rc. this is a temp solution, replacing non-smeared energy by the re-calculated energy
      //double energy_tmp = sqrt(parts[i].p.x*parts[i].p.x + parts[i].p.y*parts[i].p.y + parts[i].p.z*parts[i].p.z + parts[i].mass*parts[i].mass);//tmpsolution
      double energy_tmp = parts[i].energy;
      momenta[3].SetPxPyPzE(parts[i].p.x,  parts[i].p.y,  parts[i].p.z,  energy_tmp);
    }
    
    //search for di-lepton pair for the decay in recoil
    int daughter_pid = -1;    //unsigned
    if(daughter == "electron"){
      daughter_pid = 11;
    }else if(daughter == "muon"){
      daughter_pid = 13;
    }
    int first = -1;
    int second = -1;
    double best_mass = -999.;
    for (int i = 0 ; i < parts.size() ; ++i) {
      if( fabs(parts[i].pid)!=daughter_pid) continue;
      for (int j = i + 1 ; j < parts.size() ; ++j) {
        if( parts[j].pid!= - parts[i].pid) continue;
        ROOT::Math::PxPyPzMVector lpt_1(0.,0.,0.,0.);
        //double energy_tmp1 = sqrt(parts[i].p.x*parts[i].p.x + parts[i].p.y*parts[i].p.y + parts[i].p.z*parts[i].p.z + parts[i].mass*parts[i].mass);//tmpsolution
        double energy_tmp1 = parts[i].energy;
        lpt_1.SetPxPyPzE(parts[i].p.x, parts[i].p.y, parts[i].p.z, energy_tmp1);
        ROOT::Math::PxPyPzMVector lpt_2(0.,0.,0.,0.);
        //double energy_tmp2 = sqrt(parts[j].p.x*parts[j].p.x + parts[j].p.y*parts[j].p.y + parts[j].p.z*parts[j].p.z + parts[j].mass*parts[j].mass);//tmpsolution
        double energy_tmp2 = parts[j].energy;
        lpt_2.SetPxPyPzE(parts[j].p.x, parts[j].p.y, parts[j].p.z, energy_tmp2);        
        const double new_mass{(lpt_1 + lpt_2).mass()};
        if (fabs(new_mass - get_pdg_mass(mother)) < fabs(best_mass - get_pdg_mass(mother))) {
          first = i;
          second = j;
          best_mass = new_mass;
          momenta[5].SetPxPyPzE(parts[i].p.x, parts[i].p.y, parts[i].p.z, energy_tmp1);
          momenta[6].SetPxPyPzE(parts[j].p.x, parts[j].p.y, parts[j].p.z, energy_tmp2);
        }
        
      }
    }
    
    //FIXME search for scattered electron, need improvement with more complex events
    //float dp = 10.;
    for(int i = 0 ; i < parts.size(); i++){
      if(i==first || i==second) continue;   //skip the paired leptons
      if(parts[i].pid != 11) continue;
      //float ptmp = sqrt(parts[i].p.x*parts[i].p.x + parts[i].p.y*parts[i].p.y + parts[i].p.z*parts[i].p.z);
      //if( (k_prime.px()) * (pair_4p.px()) + (k_prime.py()) * (pair_4p.py()) + (k_prime.pz()) * (pair_4p.pz()) > 0. || ptmp >= 10.) continue; //angle between jpsi and scattered electron < pi/2, 3-momentum mag < 10. 
      //if(dp > 10.- ptmp){     //if there are more than one candidate of scattered electron, choose the one with highest 3-momentum mag
        //double energy_tmp = sqrt(parts[i].p.x*parts[i].p.x + parts[i].p.y*parts[i].p.y + parts[i].p.z*parts[i].p.z + parts[i].mass*parts[i].mass);//tmpsolution
        double energy_tmp  = parts[i].energy;
        momenta[2].SetPxPyPzE(parts[i].p.x, parts[i].p.y, parts[i].p.z, energy_tmp);
      //  dp = 10. - ptmp;
      //}
    }
    //for(int i = 0 ; i < 7 ; i++){
    //    cout<<Form("dum, idx = %d, P(px, py, pz, mass) = (%f, %f, %f, %f)", i, momenta[i].px(), momenta[i].py(), momenta[i].pz(), momenta[i].mass())<<endl;
    //}
    //cout<<"========================================="<<endl;
    return momenta;
  }
  
  inline inv_quant calc_inv_quant(const std::vector<ROOT::Math::PxPyPzMVector>& parts)
  {
    //0:e0  1:p0    2:e1    3:p1    4:recoil system (without p1)    5:l1 from 4 6:l2 from 4
    ROOT::Math::PxPyPzMVector q(parts[0] - parts[2]);
    ROOT::Math::PxPyPzMVector k(parts[0]);
    ROOT::Math::PxPyPzMVector P(parts[1]);
    ROOT::Math::PxPyPzMVector Delta(parts[3] - parts[1]);//exact
    ROOT::Math::PxPyPzMVector Delta_prime(parts[0] - parts[2] - parts[5] - parts[6]);//exclude gamma radiation in jpsi decay
    
    double    nu         = q.Dot(P) / P.mass();
    double    Q2         = -q.Dot(q);
    double t = 0.;
    //if(parts[4].px() == 0. && parts[4].py() == 0. && parts[4].pz() == 0. && parts[4].mass() == 0.){
        //t = Delta_prime.Dot(Delta_prime);
    //}else{
        t = Delta.Dot(Delta);
    //}
    double y = q.Dot(P) / k.Dot(P);
    inv_quant quantities = {nu, Q2, Q2/2./P.mass()/nu, y, t};
    return quantities;
  }
  
  
  inline double get_nu(inv_quant quantities) { return quantities.nu / 1000.; }
  inline double get_Q2(inv_quant quantities) { return quantities.Q2; }
  inline double get_x(inv_quant quantities) { return quantities.x; }
  inline double get_y(inv_quant quantities) { return quantities.y; }
  inline double get_t(inv_quant quantities) { return quantities.t; }

  // for tracking, add later

  //=========================================================================================================

} // namespace util

#endif
