import argparse
import numpy as np
import uproot as ur
from collections import namedtuple
from scipy.stats import norm
import matplotlib.pyplot as plt


def plot_energy(rec_file, out_file, out_dir):
    files = [rec_file+":events"]
    endcap_events = ur.concatenate(files, ["EcalEndcapPHitsReco.energy", "HcalEndcapPHitsReco.energy"], library = 'np')

    ecal_list = []
    hcal_list = []
    num_events = len(endcap_events["EcalEndcapPHitsReco.energy"])
    for i in range(num_events):
        ecal_energy = np.sum(endcap_events["EcalEndcapPHitsReco.energy"][i])
        hcal_energy = np.sum(endcap_events["HcalEndcapPHitsReco.energy"][i])
        if ecal_energy + hcal_energy > 0.1:
            ecal_list.append(ecal_energy)
            hcal_list.append(hcal_energy)
         
    w_list = []
    r_list = []
    w = 1
    fig, axs = plt.subplots(2, 2)
    for ax in axs.flat:
        energy_list = np.array(ecal_list)/w + np.array(hcal_list)
        
        # best fit of data
        (mu, sigma) = norm.fit(energy_list)

        # the histogram of the data
        n, bins, patches = ax.hist(energy_list, bins='auto', density=True, stacked=True, facecolor='green', alpha=0.75)

        # add a 'best fit' line
        y = norm.pdf(bins, mu, sigma)
        l = ax.plot(bins, y, 'r--', linewidth=2)

        #plot
        ax.set(xlabel="Energy (GeV)")
        ax.set_title(r"$w=%d, \mu=%.3f,\ \sigma=%.3f$" %(w, mu, sigma))
        
        w_list.append(w)
        r_list.append(sigma/mu)
        w += 1
    plt.savefig(out_dir+"/"+out_file)

    plt.clf()
    plt.xlabel("w")
    plt.ylabel(r"$\sigma/\mu$")
    plt.title(r"$\sigma/\mu$ vs w")
    plt.scatter(w_list, r_list)
    plt.savefig(out_dir+"/rw_"+out_file)


def plot_efficiency(n_file, tru_file, rec_file, out_file, out_dir):
    tru_files = []
    rec_files = []
    for proc in range(int(n_file)):
        tru_files.append(tru_file+str(proc)+".root:events")
        rec_files.append(rec_file+str(proc)+".root:events")
    tru_events = ur.concatenate(tru_files, ["EcalEndcapPClusters.energy", "EcalEndcapPClusters.eta",
                                            "EcalEndcapPMergedClusters.energy", "EcalEndcapPMergedClusters.eta"], library = 'np')
    rec_events = ur.concatenate(rec_files, ["EcalEndcapPClusters.energy", "EcalEndcapPClusters.eta",
                                            "EcalEndcapPMergedClusters.energy", "EcalEndcapPMergedClusters.eta"], library = 'np')

    min_ene = np.arange(0.1, 0.95, 0.1)
    eff_bins = np.arange(1.05, 3.5, 0.1)
    eff_center = np.arange(1.1, 3.45, 0.1)
    ene_eta = namedtuple("EneEta", ["energy", "eta"])

    tru_tracks = []
    for enes, etas in zip(tru_events["EcalEndcapPClusters.energy"], tru_events["EcalEndcapPClusters.eta"]):
        for ene, eta in zip(enes, etas):
            tru_tracks.append(ene_eta(ene, eta))
    tru_hist = np.histogram(tru_tracks, bins=eff_bins)

    rec_tracks = []
    for enes, etas in zip(rec_events["EcalEndcapPClusters.energy"], rec_events["EcalEndcapPClusters.eta"]):
        for ene, eta in zip(enes, etas):
            rec_tracks.append(ene_eta(ene, eta))
    rec_hist = np.histogram(rec_tracks, bins=eff_bins)

    merged_tru_tracks = []
    for enes, etas in zip(tru_events["EcalEndcapPMergedClusters.energy"], tru_events["EcalEndcapPMergedClusters.eta"]):
        for ene, eta in zip(enes, etas):
            merged_tru_tracks.append(ene_eta(ene, eta))

    merged_rec_tracks = []
    for enes, etas in zip(rec_events["EcalEndcapPMergedClusters.energy"], rec_events["EcalEndcapPMergedClusters.eta"]):
        for ene, eta in zip(enes, etas):
            merged_rec_tracks.append(ene_eta(ene, eta))
    merged_rec_hist = np.histogram(merged_rec_tracks, bins=eff_bins)

    fig, axs = plt.subplots(3, 3, figsize=(20,15))
    for iax in range(9):
        tru_hist = np.histogram([x.eta for x in tru_tracks if x.energy > min_ene[iax]], bins=eff_bins)
        rec_hist = np.histogram([x.eta for x in rec_tracks if x.energy > min_ene[iax]], bins=eff_bins)
        merged_tru_hist = np.histogram([x.eta for x in merged_tru_tracks if x.energy > min_ene[iax]], bins=eff_bins)
        merged_rec_hist = np.histogram([x.eta for x in merged_rec_tracks if x.energy > min_ene[iax]], bins=eff_bins)

        eff_list = np.divide(rec_hist[0], tru_hist[0])
        eff_err = np.multiply(eff_list, np.sqrt(np.divide(1., rec_hist[0]) + np.divide(1., tru_hist[0])))

        merged_eff_list = np.divide(merged_rec_hist[0], merged_tru_hist[0])
        merged_eff_err = np.multiply(merged_eff_list, np.sqrt(np.divide(1., merged_rec_hist[0]) + np.divide(1., merged_tru_hist[0])))

        tru_eff_list = np.divide(merged_tru_hist[0], tru_hist[0])
        tru_eff_err = np.multiply(tru_eff_list, np.sqrt(np.divide(1., merged_tru_hist[0]) + np.divide(1., tru_hist[0])))

        ax = axs.flat[iax]
        ax.errorbar(eff_center, eff_list, yerr=eff_err, fmt='o', color='black',
                    ecolor='black', elinewidth=1., capsize=1.5, label='Unmerged clusters')
        ax.errorbar(eff_center, merged_eff_list, yerr=merged_eff_err, fmt='s', color='red',
                    ecolor='red', elinewidth=1., capsize=1.5, label='Merged clusters')
        ax.errorbar(eff_center, tru_eff_list, yerr=tru_eff_err, fmt='^', color='green',
                    ecolor='green', elinewidth=1., capsize=1.5, label='True clusters')
        ax.set_xlabel(r"$\eta$")
        ax.set_ylabel(r"eff")
        ax.set_title(r"$E_{clus}$ > "+f"{min_ene[iax]:.1f} GeV")
        #ax.legend()
    plt.savefig(out_dir+"/"+out_file)
         

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--plot_ene', action='store_true', default=False,
                        help='Plot reco energy')
    parser.add_argument('--plot_eff', action='store_true', default=False,
                        help='Plot reco efficiency')
    parser.add_argument('--tru_file', help='Path to truth output file.')
    parser.add_argument('rec_file', help='Path to reconstruction output file.')
    parser.add_argument('out_file', help='Name of output file.')
    parser.add_argument('-o', dest='out_dir', default='results', help='Output directory.')
    parser.add_argument('-n', dest='n_file', default=1, help='Number of files.')
    args = parser.parse_args()

    if args.plot_ene:
        plot_energy(args.rec_file, args.out_file, args.out_dir)

    if args.plot_eff:
        plot_efficiency(args.n_file, args.tru_file, args.rec_file, args.out_file, args.out_dir)
