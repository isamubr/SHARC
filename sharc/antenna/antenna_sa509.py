#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Sep 10 23:03:26 2017

@author: carlosrodriguez
"""

from sharc.antenna.antenna import Antenna
from sharc.parameters.parameters_fss_es import ParametersFssEs

import numpy as np

class AntennaSA509(Antenna):
    """
    Implements the Earth station antenna pattern in the RAS service
    according to Recommendation ITU-R SA.509-6
    """
# Implementatio with no knowlegde of antenna gain    
    def __init__(self, param: ParametersFssEs):
        super().__init__()
        self.peak_gain = param.antenna_gain
        self.aperture_efficiency = 60
# INCLUDE ETA AS PARAMETER OR CONSEIDER THE MAXIMUM GAIN        
        lmbda = 3e8 / ( param.frequency * 1e6 )
        D_lmbda = param.diameter / lmbda
        G0_arg_log = self.aperture_efficiency * np.power(3.14 * D_lmbda, 2)
        self.G0 = 10 * np.log10(G0_arg_log)

# Implementation of diagram pattern for cases of multiple entry interference
        if D_lmbda >=  100:
            self.phi_0 = 20 * np.sqrt(3) / D_lmbda
            self.phi_1 = self.phi_0 * np.sqrt(20 / 3)
            self.phi_2 = np.power(10, (49 - self.G0) / 25)
        else:
            self.phi_0 = 20 * np.sqrt(3) / D_lmbda
# implement error message or alert
        
    def calculate_gain(self, *args, **kwargs) -> np.array:
        phi = np.absolute(kwargs["phi_vec"])
        
        gain = np.zeros(phi.shape)
                
        idx_0 = np.where(phi < self.phi_1)[0]
        gain[idx_0] = self.G0 - 3 * np.power(phi[idx_0] / self.phi_0, 2)
        
        idx_1 = np.where((self.phi_1 <= phi) ) & (phi < self.phi_2 )[0]
        gain[idx_1] = self.G0 - 20

        idx_2 = np.where((self.phi_2 <= phi) & (phi < 48))[0]
        gain[idx_2] = 29 - 25 * np.log10(phi[idx_2])
            
        idx_3 = np.where((48 <= phi) & (phi < 80))[0]
        gain[idx_3] = -13
 
        idx_4 = np.where((80 <= phi) & (phi < 120))[0]
        gain[idx_4] = -8
        
        idx_5 = np.where((120 <= phi) & (phi < 180))[0]
        gain[idx_5] = -13

        return gain
        
        
if __name__ == '__main__':
    import matplotlib.pyplot as plt

    phi = np.linspace(0.1, 100, num = 100000)
    
    # initialize antenna parameters
    param27 = ParametersFssEs()
    param27.antenna_pattern = "ITU-R S.509-3"
    param27.frequency = 27000
    param27.antenna_gain = 64
    param27.diameter = 9.6
    antenna27 = AntennaSA509(param27)

    gain27 = antenna27.calculate_gain(phi_vec=phi)
    
    param43 = ParametersFssEs()
    param43.antenna_pattern = "ITU-R S.509-3"
    param43.frequency = 43000
    param43.antenna_gain = 50
    param43.diameter = 1.8
    antenna43 = AntennaSA509(param43)
    gain43 = antenna43.calculate_gain(phi_vec=phi)

    fig = plt.figure(figsize=(8,7), facecolor='w', edgecolor='k')  # create a figure object
    
    plt.semilogx(phi, gain27 - param27.antenna_gain, "-b", label = "$f = 27$ $GHz,$ $D = 9.6$ $m$")
 #   plt.semilogx(phi, gain43 - param43.antenna_gain, "-r", label = "$f = 43$ $GHz,$ $D = 1.8$ $m$")

    plt.title("ITU-R SA.509 antenna radiation pattern")
    plt.xlabel("Off-axis angle $\phi$ [deg]")
    plt.ylabel("Gain relative to $G_m$ [dB]")
    plt.legend(loc="lower left")
    plt.xlim((phi[0], phi[-1]))
    plt.ylim((-80, 10))
    
    #ax = plt.gca()
    #ax.set_yticks([-30, -20, -10, 0])
    #ax.set_xticks(np.linspace(1, 9, 9).tolist() + np.linspace(10, 100, 10).tolist())

    plt.grid()
    plt.show()        