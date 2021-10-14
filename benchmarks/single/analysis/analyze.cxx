#include <iostream>
#include <string>

#include <ROOT/RDataFrame.hxx>

#include <eicd/ReconstructedParticleData.h>

int analyze(std::string file)
{
  // open dataframe
  ROOT::RDataFrame df("events", file, {"GeneratedParticles", "ReconstructedParticles"});

  // count total events
  auto count = df.Count();
  if (count == 0) {
    std::cout << "Error: No events found" << std::endl;
    return -1;
  }

  auto n_tracks = [](const std::vector<eic::ReconstructedParticleData> &p) { return (int) p.size(); };

  auto d = df
  .Define("n_tracks_gen", n_tracks, {"GeneratedParticles"})
  .Define("n_tracks_rec", n_tracks, {"ReconstructedParticles"})
  ;

  auto stats_n_tracks_gen = d.Stats("n_tracks_gen");
  auto stats_n_tracks_rec = d.Stats("n_tracks_rec");
  if (stats_n_tracks_rec->GetMean() < 0.8) {
    std::cout << "Error: too few tracks per events " << std::endl;
    stats_n_tracks_gen->Print();
    stats_n_tracks_rec->Print();
    return -1;
  }

  // success
  return 0;
}
