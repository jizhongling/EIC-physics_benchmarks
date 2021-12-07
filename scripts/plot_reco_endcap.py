import argparse
import numpy as np
import uproot as ur
from scipy.stats import norm
import matplotlib.pyplot as plt


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('rec_file', help='Path to reconstruction output file.')
    parser.add_argument('out_file', help='Name of output file.')
    parser.add_argument('-o', dest='outdir', default='.', help='Output directory.')
    args = parser.parse_args()
    
    files = [args.rec_file+":events"]
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
        
    plt.savefig(args.outdir+"/"+args.out_file)
    plt.clf()
    plt.xlabel("w")
    plt.ylabel(r"$\sigma/\mu$")
    plt.title(r"$\sigma/\mu$ vs w")
    plt.scatter(w_list, r_list)
    plt.savefig(args.outdir+"/rw_"+args.out_file)
