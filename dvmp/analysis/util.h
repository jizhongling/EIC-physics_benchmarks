#ifndef UTIL_H
#define UTIL_H

#include <algorithm>
#include <cmath>
#include <exception>
#include <fmt/core.h>
#include <limits>
#include <string>
#include <vector>

#include <Math/Vector4D.h>

#include "dd4pod/Geant4ParticleCollection.h"
#include "eicd/TrackParametersCollection.h"

namespace util {

// Exception definition for unknown particle errors
// FIXME: A utility exception base class should be included in the analysis
//        utility library, so we can skip most of this boilerplate
class unknown_particle_error : public std::exception {
public:
  unknown_particle_error(std::string_view particle) : m_particle{particle} {}
  virtual const char* what() const throw() {
    return fmt::format("Unknown particle type: {}", m_particle).c_str();
  }
  virtual const char* type() const throw() { return "unknown_particle_error"; }

private:
  const std::string m_particle;
};

// Simple function to return the appropriate PDG mass for the particles
// we care about for this process.
// FIXME: consider something more robust (maybe based on hepPDT) to the
//        analysis utility library
inline double get_pdg_mass(std::string_view part) {
  if (part == "electron") {
    return 0.0005109989461;
  } else if (part == "muon") {
    return .1056583745;
  } else if (part == "jpsi") {
    return 3.0969;
  } else if (part == "upsilon") {
    return 9.49630;
  } else {
    throw unknown_particle_error{part};
  }
}

// Get a vector of 4-momenta from raw tracking info, using an externally
// provided particle mass assumption.
// FIXME: should be part of utility library
inline auto
momenta_from_tracking(const std::vector<eic::TrackParametersData>& tracks,
                      const double mass) {
  std::vector<ROOT::Math::PxPyPzMVector> momenta{tracks.size()};
  // transform our raw tracker info into proper 4-momenta
  std::transform(tracks.begin(), tracks.end(), momenta.begin(),
                 [mass](const auto& track) {
                   // make sure we don't divide by zero
                   if (fabs(track.qOverP) < 1e-9) {
                     return ROOT::Math::PxPyPzMVector{};
                   }
                   const double p = fabs(1. / track.qOverP);
                   const double px = p * cos(track.phi) * sin(track.theta);
                   const double py = p * sin(track.phi) * sin(track.theta);
                   const double pz = p * cos(track.theta);
                   return ROOT::Math::PxPyPzMVector{px, py, pz, mass};
                 });
  return momenta;
}

// Get a vector of 4-momenta from the simulation data.
// FIXME: should be part of utility library
// TODO: Add PID selector (maybe using ranges?)
inline auto
momenta_from_simulation(const std::vector<dd4pod::Geant4ParticleData>& parts) {
  std::vector<ROOT::Math::PxPyPzMVector> momenta{parts.size()};
  // transform our simulation particle data into 4-momenta
  std::transform(parts.begin(), parts.end(), momenta.begin(),
                 [](const auto& part) {
                   return ROOT::Math::PxPyPzMVector{part.psx, part.psy,
                                                    part.psz, part.mass};
                 });
  return momenta;
}

// Find the decay pair candidates from a vector of particles (parts),
// with invariant mass closest to a desired value (pdg_mass)
// FIXME: not sure if this belongs here, or in the utility library. Probably the
//        utility library
inline std::pair<ROOT::Math::PxPyPzMVector, ROOT::Math::PxPyPzMVector>
find_decay_pair(const std::vector<ROOT::Math::PxPyPzMVector>& parts,
                const double pdg_mass) {
  int first = -1;
  int second = -1;
  double best_mass = -1;

  // go through all particle combinatorics, calculate the invariant mass
  // for each combination, and remember which combination is the closest
  // to the desired pdg_mass
  for (int i = 0; i < parts.size(); ++i) {
    for (int j = i + 1; j < parts.size(); ++j) {
      const double new_mass{(parts[i] + parts[j]).mass()};
      if (fabs(new_mass - pdg_mass) < fabs(best_mass - pdg_mass)) {
        first = i;
        second = j;
        best_mass = new_mass;
      }
    }
  }
  if (first < 0) {
    return {{}, {}};
  }
  return {parts[first], parts[second]};
}

// Calculate the invariant mass of a given pair of particles
inline double
get_im(const std::pair<ROOT::Math::PxPyPzMVector, ROOT::Math::PxPyPzMVector>&
           particle_pair) {
  return (particle_pair.first + particle_pair.second).mass();
}

// Calculate the transverse momentum of a given pair of particles
inline double
get_pt(const std::pair<ROOT::Math::PxPyPzMVector, ROOT::Math::PxPyPzMVector>&
           particle_pair) {
  double px_pair = (particle_pair.first + particle_pair.second).px();
  double py_pair = (particle_pair.first + particle_pair.second).py();  
  return sqrt(px_pair*px_pair + py_pair*py_pair);
}

// Calculate the azimuthal angle of a given pair of particles
inline double
get_phi(const std::pair<ROOT::Math::PxPyPzMVector, ROOT::Math::PxPyPzMVector>&
           particle_pair) {
  double px_pair = (particle_pair.first + particle_pair.second).px();
  double py_pair = (particle_pair.first + particle_pair.second).py();
  double phi_pair = std::atan2(py_pair,px_pair);
  //if(py_pair <= 0.) phi_pair = - phi_pair;
  return phi_pair;
}

// Calculate the rapidity of a given pair of particles
inline double
get_y(const std::pair<ROOT::Math::PxPyPzMVector, ROOT::Math::PxPyPzMVector>&
           particle_pair) {
  double px_pair = (particle_pair.first + particle_pair.second).px();
  double py_pair = (particle_pair.first + particle_pair.second).py();
  double pz_pair = (particle_pair.first + particle_pair.second).pz();
  double mass_pair = (particle_pair.first + particle_pair.second).mass();
  double energy_pair = sqrt(mass_pair*mass_pair + px_pair*px_pair + py_pair*py_pair + pz_pair*pz_pair);
  return 0.5*log((energy_pair + pz_pair)/(energy_pair - pz_pair));
}

//========================================================================================================
//for structure functions

struct inv_quant{    //add more when needed
    double nu, Q2, x;
};

//for simu
inline inv_quant calc_inv_quant_simu(const std::vector<ROOT::Math::PxPyPzMVector>& parts){
  ROOT::Math::PxPyPzMVector q(parts[0] - parts[2]);
  ROOT::Math::PxPyPzMVector P(parts[3]);
  
  double nu = q.Dot(P) / P.mass();
  double Q2 = - q.Dot(q);  
  inv_quant quantities = {nu, Q2, Q2/2./P.mass()/nu};
  return quantities;
}

inline double get_nu_simu(inv_quant quantities) {
  return quantities.nu/1000.;
}
inline double get_Q2_simu(inv_quant quantities) {
  return quantities.Q2;
}
inline double get_x_simu(inv_quant quantities) {
  return quantities.x;
}

//for tracking, add later

//=========================================================================================================






} // namespace util

#endif
