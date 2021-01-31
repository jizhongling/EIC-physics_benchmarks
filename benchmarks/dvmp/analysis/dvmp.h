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

  // Calculate the 4-vector sum of a given pair of particles
  inline ROOT::Math::PxPyPzMVector
  get_sum(const std::pair<ROOT::Math::PxPyPzMVector, ROOT::Math::PxPyPzMVector>& particle_pair)
  {
    return (particle_pair.first + particle_pair.second);
  }

  //========================================================================================================
  // for structure functions

  struct inv_quant { // add more when needed
    double nu, Q2, x;
  };

  // for simu
  inline inv_quant calc_inv_quant_simu(const std::vector<ROOT::Math::PxPyPzMVector>& parts)
  {
    ROOT::Math::PxPyPzMVector q(parts[0] - parts[2]);
    ROOT::Math::PxPyPzMVector P(parts[3]);

    double    nu         = q.Dot(P) / P.mass();
    double    Q2         = -q.Dot(q);
    inv_quant quantities = {nu, Q2, Q2 / 2. / P.mass() / nu};
    return quantities;
  }

  inline double get_nu_simu(inv_quant quantities) { return quantities.nu / 1000.; }
  inline double get_Q2_simu(inv_quant quantities) { return quantities.Q2; }
  inline double get_x_simu(inv_quant quantities) { return quantities.x; }

  // for tracking, add later

  //=========================================================================================================

} // namespace util

#endif
