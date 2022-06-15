#!/usr/bin/env python
# coding: utf-8

import os
import numpy as np
import uproot as ur
import awkward as ak
import matplotlib.pyplot as plt
import matplotlib as mpl
import mplhep 
import argparse



parser = argparse.ArgumentParser()
parser.add_argument('--rec_file', type=str, help='Reconstructed track file.')
parser.add_argument('--ebeam', type=float, help='Electron beam energy.')
parser.add_argument('--pbeam', type=float, help='Proton (or ion) beam energy.')
parser.add_argument('--minq2', type=float, help='Minimum four-momentum transfer squared Q2.')
parser.add_argument('-o', dest='outdir', default='results/dis/', help='Output directory.')
args = parser.parse_args()
kwargs = vars(args)

rec_file = args.rec_file
minq2 = int(args.minq2)
k = int(args.ebeam)
p = int(args.pbeam)



#logarithmically spaced bins in Q2 and 𝑥 
Q2_bins = [0.40938507,0.64786184,1.025353587,1.626191868,2.581181894,4.091148983,6.478618696,10.25353599,16.26191868,25.81181894,40.91148983,64.78618696,102.5353599,162.6191868,258.1181894,409.1148983,647.8618696,1025.353599,1626.191868,2581.181894,4091.148983,6482.897648]
x_bins = [4.09385E-05,6.47862E-05,0.000102535,0.000162619,0.000258118,0.000409115,0.000647862,0.001025354,0.001626192,0.002581182,0.004091149,0.006478619,0.010253536,0.016261919,0.025811819,0.04091149,0.064786187,0.10253536,0.162619187,0.25811819,0.409114898,0.647861868,1.025257131]



#function to construct Q2 correlation plots
def Q2correlation(minq2,method): #minq2 can be 1,10,100, or 1000; method can be 'e','DA', or 'JB'

    Q2values_Y = method_Q2values_dict['{}'.format(method)]  #Q2 values of the given method, that are mapped onto the y axis 
    
    Q2_List_T = Q2values_T #Truth Q2 values, mapped along x axis
    Q2_List_Y = Q2values_Y #method (E/DA/JB) Q2 values, mapped along y axis

    T_len = ak.count(Q2_List_T,axis=0) #total number of events in Truth
    Y_len = ak.count(Q2_List_Y,axis=0) #total number of events in method

    if T_len > Y_len: #if total number of events for Truth is greater
        Y_boolean = ak.count(Q2_List_Y,axis=-1) >= 1 #boolean to filter ak.Arrays wrt single events in method 
        Q2_List_T_F = Q2_List_T[Y_boolean] #filtered Truth Q2 values
        Q2_List_Y_F = Q2_List_Y[Y_boolean] #filtered method Q2 values
    else: #if total number of events for method is greater
        T_boolean = ak.count(Q2_List_T,axis=-1) >= 1 #boolean to filter ak.Arrays wrt single events in Truth
        Q2_List_T_F = Q2_List_T[T_boolean] #filtered Truth Q2 values
        Q2_List_Y_F = Q2_List_Y[T_boolean] #filtered method Q2 values
    
    T_Q2s = np.array(ak.flatten(Q2_List_T_F)) #Truth Q2 values, mapped along x axis
    Y_Q2s = np.array(ak.flatten(Q2_List_Y_F)) #method Q2 values, mapped along y axis
    
    #2-dimensional histogram, h
    h, xedges, yedges = np.histogram2d(x=T_Q2s,y=Y_Q2s, bins=[Q2_bins,Q2_bins]) 

    minq2_dict = {'1':2,'10':7,'100':12,'1000':17} #Q2 bin index at which minq2 starts
    h[0:minq2_dict['{}'.format(minq2)]]=0 #ignore values before minq2

    #normalization of h:
    col_sum = ak.sum(h,axis=-1) #number of events in each (verticle) column 
    norm_h = [] #norm_h is the normalized matrix
    norm_h_text = [] #display labels matrix
    for i in range(len(col_sum)):
        if col_sum[i] != 0:
            norm_c = h[i]/col_sum[i] #normalized column = column values divide by sum of the column
        else:
            norm_c = h[i]
        norm_h.append(norm_c)
        norm_c_text = [ '%.3f' % elem for elem in norm_c ] #display value to 3 dp
        norm_h_text.append(norm_c_text)
    
    fig = plt.figure()
    mplhep.hist2dplot(H=norm_h,norm=mpl.colors.LogNorm(vmin= 1e-4, vmax= 1),labels=norm_h_text,xbins=Q2_bins,ybins=Q2_bins)
    plt.yscale('log')
    plt.xscale('log')
    fig.set_figwidth(11)
    fig.set_figheight(11)
    plt.xlabel('$Q^2$ [$GeV^2$] Truth')
    plt.ylabel('$Q^2$ [$GeV^2$] {}'.format(method_dict['{}'.format(method)]))
    plt.title('{}   $Q^2$ correlation   {}x{}   $minQ^2=${}$GeV^2$'.format(method_dict['{}'.format(method)],k,p,minq2))
    plt.show()
    plt.savefig(os.path.join(args.outdir, '%gon%g/minQ2=%g/Q2_correlation_%s_%gx%g_minQ2=%g.png' %(k,p,minq2,method,k,p,minq2)))



#function to construct Bjorken-x correlation plots
def Xcorrelation(minq2,method): #minq2 can be 1,10,100, or 1000; method can be 'e','DA', or 'JB'

    Xvalues_Y = method_Xvalues_dict['{}'.format(method)] #x values of the given method, that are mapped onto the y axis 
        
    X_List_T = Xvalues_T #Truth x values, mapped along x axis
    X_List_Y = Xvalues_Y #method (E/DA/JB) x values, mapped along y axis

    T_len = ak.count(X_List_T,axis=0) #total number of events in Truth
    Y_len = ak.count(X_List_Y,axis=0) #total number of events in method

    if T_len > Y_len: #if total number of events for Truth is greater
        Y_boolean = ak.count(X_List_Y,axis=-1) >= 1 #boolean to filter ak.Arrays wrt single events in method 
        X_List_T_F = X_List_T[Y_boolean] #filtered Truth x values
        X_List_Y_F = X_List_Y[Y_boolean] #filtered method x values
    else: #if total number of events for method is greater
        T_boolean = ak.count(X_List_T,axis=-1) >= 1 #boolean to filter ak.Arrays wrt single events in Truth
        X_List_T_F = X_List_T[T_boolean] #filtered Truth x values
        X_List_Y_F = X_List_Y[T_boolean] #filtered method x values
    
    T_Xs = np.array(ak.flatten(X_List_T_F)) #Truth Bjorken-x values, mapped along x axis
    Y_Xs = np.array(ak.flatten(X_List_Y_F)) #method Bjorken-x values, mapped along y axis
    
    T_x_bool = T_Xs>=minq2/(4*k*p) #boolean to filter x values that satisfy bjorken-x equation for minq2, ebeam and pbeam
    T_Xs = T_Xs[T_x_bool]
    Y_Xs = Y_Xs[T_x_bool]

    #2-dimensional histogram, h
    h, xedges, yedges = np.histogram2d(x=T_Xs,y=Y_Xs, bins=[x_bins,x_bins])
    
    #normalization of h:
    col_sum = ak.sum(h,axis=-1) #number of events in each (verticle) column 
    norm_h = [] #norm_h is the normalized matrix
    norm_h_text = [] #display labels matrix
    for i in range(len(col_sum)):
        if col_sum[i] != 0:
            norm_c = h[i]/col_sum[i] #normalized column = column values divide by sum of the column
        else:
            norm_c = h[i]
        norm_h.append(norm_c)
        norm_c_text = [ '%.2f' % elem for elem in norm_c ] #display value to 2 dp
        norm_h_text.append(norm_c_text)

    fig = plt.figure()
    mplhep.hist2dplot(H=norm_h,norm=mpl.colors.LogNorm(vmin= 1e-4, vmax= 1),labels=norm_h_text,xbins=x_bins,ybins=x_bins)
    plt.yscale('log')
    plt.xscale('log')
    fig.set_figwidth(11)
    fig.set_figheight(11)
    plt.xlabel('x Truth')
    plt.ylabel('$x$   {}'.format(method_dict['{}'.format(method)]))
    plt.title('{}   $x$ correlation   {}x{}   $minQ^2=${}$GeV^2$'.format(method_dict['{}'.format(method)],k,p,minq2))
    plt.show()
    plt.savefig(os.path.join(args.outdir, '%gon%g/minQ2=%g/x_correlation_%s_%gx%g_minQ2=%g.png' %(k,p,minq2,method,k,p,minq2)))



keys = ur.concatenate(rec_file + ':events/' + 'InclusiveKinematicsTruth')
Truth =   [keys['InclusiveKinematicsTruth.Q2'],keys['InclusiveKinematicsTruth.x']]
keys = ur.concatenate(rec_file + ':events/' + 'InclusiveKinematicsElectron')
Electron =   [keys['InclusiveKinematicsElectron.Q2'], keys['InclusiveKinematicsElectron.x']]
keys = ur.concatenate(rec_file + ':events/' + 'InclusiveKinematicsDA')
DoubleAngle =  [keys['InclusiveKinematicsDA.Q2'], keys['InclusiveKinematicsDA.x']]
keys = ur.concatenate(rec_file + ':events/' + 'InclusiveKinematicsJB')
JacquetBlondel =  [keys['InclusiveKinematicsJB.Q2'], keys['InclusiveKinematicsJB.x']]

Q2values_T = Truth[0]
Q2values_E = Electron[0]
Q2values_DA = DoubleAngle[0]
Q2values_JB = JacquetBlondel[0]
Xvalues_T = Truth[1]
Xvalues_E = Electron[1]
Xvalues_DA = DoubleAngle[1]
Xvalues_JB = JacquetBlondel[1]

method_dict = {'e':'Electron','DA':'Double-Angle','JB':'Jacquet-Blondel'}
method_Q2values_dict = {'e':Q2values_E,'DA':Q2values_DA,'JB':Q2values_JB}
method_Xvalues_dict = {'e':Xvalues_E,'DA':Xvalues_DA,'JB':Xvalues_JB}

Q2correlation(minq2,'e')
Xcorrelation(minq2,'e')
Q2correlation(minq2,'DA')
Xcorrelation(minq2,'DA')
Q2correlation(minq2,'JB')
Xcorrelation(minq2,'JB')
