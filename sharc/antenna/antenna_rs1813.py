#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Sep 10 23:47:15 2017

@author: carlosrodriguez
"""

from sharc.antenna.antenna import Antenna
from sharc.parameters.parameters_fss_es import ParametersFssEs

import numpy as np

class AntennaRS1813(Antenna):
    """
    Implements the spaceborne sensor antenna pattern in the EESS (passive) service
    according to Recommendation ITU-R RS.1813-1
    """
# Implementatio with no knowlegde of antenna gain    
    def __init__(self, param: ParametersFssEs):
        super().__init__()
        self.peak_gain = param.antenna_gain
        self.aperture_efficiency = 60
# INCLUDE ETA AS PARAMETER OR CONSEIDER THE MAXIMUM GAIN        
        lmbda = 3e8 / ( param.frequency * 1e6 )
        self.D_lmbda = param.diameter / lmbda
        Gmax_arg_log = self.aperture_efficiency * np.power(3.14 * self.D_lmbda, 2)
        self.Gmax = 10 * np.log10(Gmax_arg_log)

# Implementation of diagram pattern for cases of multiple entry interference
        if self.D_lmbda >=  2:
            self.phi_m = 22 / self.D_lmbda * np.sqrt(5.5 * 5 * np.log10(self.D_lmbda * np.power(self.aperture_efficiency,2)))
        else:
            self.phi_m = 1
# implement error message or alert
        
    def calculate_gain(self, *args, **kwargs) -> np.array:
        phi = np.absolute(kwargs["phi_vec"])
        
        gain = np.zeros(phi.shape)
                    
        idx_0 = np.where(phi < self.phi_m)[0]
        gain[idx_0] = np.maximum(self.Gmax - 0.0018 * np.power(phi[idx_0] * self.D_lmbda, 2),-23)
        
        idx_1 = np.where((self.phi_m <= phi) ) & (phi < 69 )[0]
        gain[idx_1] = np.maximum(np.maximum(self.Gmax - 0.0018 * np.power(phi[idx_1] * self.D_lmbda, 2), 33 - 5 * np.log10(self.D_lmbda) - 25 * np.log10(phi[idx_1])),-23)

        idx_2 = np.where((self.phi_m <= phi) & (phi < 48))[0]
        gain[idx_2] = -13 - 5 * np.log10(self.D_lmbda)
            

        return gain
        
        
if __name__ == '__main__':
    import matplotlib.pyplot as plt

    phi = np.linspace(0.1, 100, num = 100000)
    
    # initialize antenna parameters
    param27 = ParametersFssEs()
    param27.antenna_pattern = "ITU-R RS.1813-1"
    param27.frequency = 27000
    param27.antenna_gain = 64
    param27.diameter = 9.6
    antenna27 = AntennaRS1813(param27)

    gain27 = antenna27.calculate_gain(phi_vec=phi)
    
    param43 = ParametersFssEs()
    param43.antenna_pattern = "ITU-R RS.1813-1"
    param43.frequency = 43000
    param43.antenna_gain = 50
    param43.diameter = 1.8
    antenna43 = AntennaRS1813(param43)
    gain43 = antenna43.calculate_gain(phi_vec=phi)

    fig = plt.figure(figsize=(8,7), facecolor='w', edgecolor='k')  # create a figure object
    
    plt.semilogx(phi, gain27 - param27.antenna_gain, "-b", label = "$f = 27$ $GHz,$ $D = 9.6$ $m$")
 #   plt.semilogx(phi, gain43 - param43.antenna_gain, "-r", label = "$f = 43$ $GHz,$ $D = 1.8$ $m$")

    plt.title("ITU-R RS.1813-1 antenna radiation pattern")
    plt.xlabel("Off-axis angle $\phi$ [deg]")
    plt.ylabel("Gain relative to $G_m$ [dB]")
    plt.legend(loc="lower left")
    plt.xlim((phi[0], phi[-1]))
    plt.ylim((-120, 10))
    
    #ax = plt.gca()
    #ax.set_yticks([-30, -20, -10, 0])
    #ax.set_xticks(np.linspace(1, 9, 9).tolist() + np.linspace(10, 100, 10).tolist())

    plt.grid()
    plt.show()        